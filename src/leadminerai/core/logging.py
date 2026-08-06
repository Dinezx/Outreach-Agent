from __future__ import annotations

import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(settings) -> None:
    logging.basicConfig(handlers=[InterceptHandler()], level=settings.log_level, force=True)
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        serialize=settings.log_serialize,
        backtrace=True,
        diagnose=False,
    )
