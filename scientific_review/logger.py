# logger.py
import logging

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def get_logger(name: str):
    return logging.getLogger(name)

if __name__ == "__main__":
    setup_logging()
    logger = get_logger(__name__)

    logger.info("Starting pipeline")