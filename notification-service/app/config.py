import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # RabbitMQ
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "audio_ready")
    RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_RETRY_DELAY_SECONDS = int(os.getenv("RABBITMQ_RETRY_DELAY_SECONDS", "3"))

    # Storage (MinIO)
    S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000").rstrip("/")
    S3_BUCKET = os.getenv("OUTPUT_BUCKET", "audios")


settings = Settings()
