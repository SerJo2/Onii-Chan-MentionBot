import logging


def base_logger(name, log_file, level=logging.INFO):
    """Sets up a logger with the specified name, file, and level."""
    logging.basicConfig(
        filename='app.log',  # Имя файла для логов
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'  # Явно указываем кодировку
    )
    handler = logging.FileHandler(log_file)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
