# logging_setup.py

import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file='processing_debug.log'):
    """
    Sets up the logging configuration with a rotating file handler.
    
    Parameters:
        log_file (str): The name of the log file.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)  # 5MB per file, keep 2 backups
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
