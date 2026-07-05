import logging
import sys
from pythonjsonlogger import jsonlogger

from app.core.config import settings


def setup_logging():
    """
    Configures structured JSON logging so logs are easy to ship to any
    log aggregator later (Render/Railway logs, or a hosted service like
    Better Stack / Papertrail) without changing application code.
    """
    logger = logging.getLogger("smartfit")
    logger.setLevel(settings.log_level)

    # Avoid duplicate handlers on reload
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logging()
