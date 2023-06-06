import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(logger_name, log_dir, filename, level=logging.INFO):
    # Create necessary directories if they don't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set up the logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    handler = RotatingFileHandler(os.path.join(log_dir, filename), maxBytes=2000, backupCount=5)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger