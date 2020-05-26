import logging
from coffeebot import config
from pythonjsonlogger import jsonlogger


def init_logger():
    logger = logging.getLogger()
    logHandler = logging.StreamHandler()
    format_str = '%(asctime)%(levelname)%(message)'
    formatter = jsonlogger.JsonFormatter(format_str)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
    return logger


logger = init_logger()
