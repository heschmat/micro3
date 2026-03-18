import pika
import json
from app.config import settings
from app.logger import setup_logger

logger = setup_logger()

def publish_message(message: dict):
    """
    Sends message to RabbitMQ queue
    """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        )
        channel = connection.channel()

        # Ensure queue exists
        channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)

        logger.info(f"Publishing message: {message}")

        channel.basic_publish(
            exchange="",
            routing_key=settings.RABBITMQ_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ),
        )

        connection.close()

        logger.info("Message published successfully")

    except Exception as e:
        logger.error(f"Failed to publish message: {e}")
        raise
