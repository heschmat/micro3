import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # RabbitMQ
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "audio_ready")

    # Storage (MinIO)
    S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    S3_BUCKET = os.getenv("OUTPUT_BUCKET", "audios")

settings = Settings()
