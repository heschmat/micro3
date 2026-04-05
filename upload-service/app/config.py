import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Internal S3 / MinIO endpoint for container-to-container traffic.
    # Example: http://minio:9000
    S3_ENDPOINT = os.getenv("S3_ENDPOINT")

    # Public/browser-facing endpoint used when generating presigned URLs.
    # Example: http://localhost:9000
    S3_PUBLIC_ENDPOINT = os.getenv("S3_PUBLIC_ENDPOINT", os.getenv("S3_ENDPOINT"))

    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")

    # Source upload bucket for original videos.
    S3_BUCKET = os.getenv("S3_BUCKET")

    # Output bucket for converted audio files.
    # Falls back to OUTPUT_BUCKET, then S3_BUCKET if not explicitly set.
    OUTPUT_S3_BUCKET = (
        os.getenv("OUTPUT_S3_BUCKET")
        or os.getenv("OUTPUT_BUCKET")
        or os.getenv("S3_BUCKET")
    )

    # RabbitMQ
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "video_jobs")
    RABBITMQ_DLQ = os.getenv("RABBITMQ_DLQ", "video_jobs_dlq")

    # App
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "500"))
    DOWNLOAD_URL_EXPIRES_SECONDS = int(
        os.getenv("DOWNLOAD_URL_EXPIRES_SECONDS", "900")
    )


settings = Settings()
