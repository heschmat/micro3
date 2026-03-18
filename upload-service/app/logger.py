import logging

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    )

    # Reduce noise from pika
    logging.getLogger("pika").setLevel(logging.WARNING)

    return logging.getLogger("upload-service")
