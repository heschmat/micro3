import boto3
from app.config import settings
from app.logger import setup_logger

logger = setup_logger()


# Internal client used by backend services inside Docker.
internal_s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

# Public-facing client used only for generating presigned URLs that
# the browser can actually open.
public_s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_PUBLIC_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)


def upload_file(file_obj, file_name: str) -> None:
    """
    Upload a file-like object to the configured source bucket.
    """
    try:
        logger.info(f"Uploading file to S3: {file_name}")

        internal_s3_client.upload_fileobj(
            file_obj,
            settings.S3_BUCKET,
            file_name,
        )

        logger.info(f"Upload successful: {file_name}")

    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise


def generate_presigned_download_url(
    object_name: str,
    expires_in: int | None = None,
) -> str:
    """
    Generate a temporary download URL for a converted audio object.

    This uses the configured OUTPUT_S3_BUCKET because converted MP3 files
    are stored in the output bucket, not the original upload bucket.
    """
    expiration = expires_in or settings.DOWNLOAD_URL_EXPIRES_SECONDS

    try:
        logger.info(
            "Generating presigned download URL for bucket=%s object=%s expires_in=%s public_endpoint=%s",
            settings.OUTPUT_S3_BUCKET,
            object_name,
            expiration,
            settings.S3_PUBLIC_ENDPOINT,
        )

        return public_s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.OUTPUT_S3_BUCKET,
                "Key": object_name,
            },
            ExpiresIn=expiration,
        )

    except Exception as e:
        logger.error(f"Failed to generate presigned URL for {object_name}: {e}")
        raise