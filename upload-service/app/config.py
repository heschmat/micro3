import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # S3 / MinIO
    S3_ENDPOINT = os.getenv("S3_ENDPOINT")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
    S3_BUCKET = os.getenv("S3_BUCKET")

    # RabbitMQ
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")

settings = Settings()
