import logging
import sys

FORMAT = '[%(asctime)s] %(levelname)s:PID-%(process)d:%(threadName)s:%(name)s: %(message)s'
LOGGING_LEVEL = logging.INFO


def get_logger(name, fmt=None, log_filename=None):
    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_LEVEL)

    if not logger.handlers:
        logging_format = fmt if fmt else FORMAT
        log_formatter = logging.Formatter(logging_format)

        if log_filename:
            file_handler = logging.FileHandler(log_filename)
            file_handler.setFormatter(log_formatter)
            # file_handler.setLevel(LOGGING_LEVEL)

        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(log_formatter)
        # stream_handler.setLevel(LOGGING_LEVEL)

        if log_filename:
            logger.addHandler(file_handler)

        logger.addHandler(stream_handler)

    return logger

# def get_logger(name):
#     logging.basicConfig(
#         level=logging.INFO,
#         format='[%(threadName)s] %(asctime)s: %(message)s',
#         stream=sys.stdout
#     )
#     return logging.getLogger(name)
