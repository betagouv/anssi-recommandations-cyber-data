import logging


def log(nom_logger: str, message: str):
    logger = logging.getLogger(nom_logger)
    logger.info(f"{message}")
