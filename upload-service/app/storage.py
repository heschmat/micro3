import boto3
from app.config import settings
from app.logger import setup_logger

logger = setup_logger()

# Create S3 client (works with MinIO)
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

def upload_file(file_obj, file_name: str):
    """
    Uploads file to MinIO/S3.
    file_obj is a file-like object (FastAPI UploadFile.file)
    """
    try:
        logger.info(f"Uploading file to S3: {file_name}")

        s3_client.upload_fileobj(
            file_obj,
            settings.S3_BUCKET,
            file_name
        )

        logger.info(f"Upload successful: {file_name}")

    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise
