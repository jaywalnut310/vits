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

        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(log_formatter)

        if log_filename:
            logger.addHandler(file_handler)

        logger.addHandler(stream_handler)

    return logger


def summarize(writer, global_step, scalars={}, histograms={}, images={}, audios={}, audio_sample_rate=22050):
    for k, v in scalars.items():
        writer.add_scalar(k, v, global_step)
    for k, v in histograms.items():
        writer.add_histogram(k, v, global_step)
    for k, v in images.items():
        writer.add_image(k, v, global_step, dataformats='HWC')
    for k, v in audios.items():
        writer.add_audio(k, v, global_step, audio_sample_rate)
