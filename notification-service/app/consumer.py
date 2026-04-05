import json
import threading
import time

import pika

from app.config import settings
from app.logger import logger


class ConsumerState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.running = False
        self.connected = False
        self.last_error: str | None = None

    def set_state(
        self,
        *,
        running: bool | None = None,
        connected: bool | None = None,
        last_error: str | None = None,
    ) -> None:
        with self.lock:
            if running is not None:
                self.running = running
            if connected is not None:
                self.connected = connected
            self.last_error = last_error

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "running": self.running,
                "connected": self.connected,
                "last_error": self.last_error,
            }


consumer_state = ConsumerState()


def _build_connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USERNAME,
        settings.RABBITMQ_PASSWORD,
    )

    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=30,
        blocked_connection_timeout=30,
    )

    return pika.BlockingConnection(parameters)


def _process_message(body: bytes) -> None:
    msg = json.loads(body)
    video_id = msg.get("video_id")
    audio_path = msg.get("audio_path")

    if not video_id:
        raise ValueError("Missing video_id in message")

    if not audio_path:
        raise ValueError("Missing audio_path in message")

    download_url = f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{audio_path}"

    logger.info(f"Download ready for video {video_id}: {download_url}")

    # Future extension point:
    # - send email
    # - publish websocket event
    # - call webhook
    # - persist notification


def start_consumer() -> None:
    consumer_state.set_state(running=True, connected=False, last_error=None)

    while True:
        connection = None
        try:
            logger.info(
                "Connecting to RabbitMQ at %s:%s...",
                settings.RABBITMQ_HOST,
                settings.RABBITMQ_PORT,
            )
            connection = _build_connection()
            channel = connection.channel()
            channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)
            channel.basic_qos(prefetch_count=1)

            consumer_state.set_state(connected=True, last_error=None)
            logger.info(f"Listening for messages on {settings.RABBITMQ_QUEUE}...")

            def callback(ch, method, properties, body):
                try:
                    _process_message(body)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                except ValueError as e:
                    logger.error(f"Invalid message payload: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                except Exception as e:
                    logger.exception(f"Failed to process message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

            channel.basic_consume(
                queue=settings.RABBITMQ_QUEUE,
                on_message_callback=callback,
            )
            channel.start_consuming()

        except Exception as e:
            logger.warning(f"RabbitMQ consumer error: {e}")
            consumer_state.set_state(
                connected=False,
                last_error=str(e),
            )
            time.sleep(settings.RABBITMQ_RETRY_DELAY_SECONDS)
        finally:
            try:
                if connection and connection.is_open:
                    connection.close()
            except Exception:
                pass
