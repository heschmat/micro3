import pika
import json
from app.config import settings
from app.logger import logger

def start_consumer():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)

    logger.info(f"Listening for messages on {settings.RABBITMQ_QUEUE}...")

    def callback(ch, method, properties, body):
        try:
            msg = json.loads(body)
            video_id = msg.get("video_id")
            audio_path = msg.get("audio_path")

            download_url = f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{audio_path}"

            logger.info(f"Download ready for video {video_id}: {download_url}")

            # In real system: could send email, websocket, push, etc.

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue=settings.RABBITMQ_QUEUE, on_message_callback=callback)
    channel.start_consuming()
