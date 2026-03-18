import logging

def get_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    )
    # reduce pika noise
    logging.getLogger("pika").setLevel(logging.WARNING)
    return logging.getLogger("notification-service")

logger = get_logger()
