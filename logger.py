# logger_config.py
import logging


def setup_logger(name, log_file, level=logging.INFO):
    """Sets up a logger with the specified name, file, and level."""
    formatter = logging.Formatter('Onii-Chain MentionBot: %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


# Example usage
baseLogger = setup_logger('Onii-Chan', 'Onii-Chan.log')