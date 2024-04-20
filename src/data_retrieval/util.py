import logging
import os
from typing import Any


def setup_output_path(output_path: str):
    """Setting up the output path (UNIX)"""
    os.makedirs(output_path, exist_ok=True)


def get_logger(
    name: str, *, log_lvl: Any = logging.DEBUG, format: str = None
) -> logging.Logger:
    logger: logging.Logger = logging.getLogger(name)
    log_format: str = (
        format if format else "%(levelname)s,%(name)s,%(asctime)s,%(message)s"
    )
    formatter = logging.Formatter(log_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.setLevel(log_lvl)

    return logger
