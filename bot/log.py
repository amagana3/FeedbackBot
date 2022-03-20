import logging
import logging.handlers


def setup_logger(name) -> logging.Logger:
    # Logger settings
    log_format = '%(levelname)s - %(funcName)s:%(lineno)d - %(message)s'

    # Setup logger
    logging.basicConfig(format=log_format, level=logging.INFO)
    logger = logging.getLogger(name)

    return logger
