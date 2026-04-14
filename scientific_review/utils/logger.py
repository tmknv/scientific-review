# scientific_review/utils/logger.py
# логирование

import logging


def setup_logging(level=logging.INFO):
    """
    Настраивает базовую конфигурацию логирования для всего приложения.

    Args:
        level: Уровень логирования (по умолчанию используется logging.INFO)
    """
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    """
    Создает и возвращает экземпляр логгера с указанным именем.

    Args:
        name: Имя логгера

    Returns:
        logging.Logger: Настроенный объект логгера
    """
    return logging.getLogger(name)


if __name__ == "__main__":
    setup_logging()
    logger = get_logger(__name__)

    logger.info("Starting pipeline")
