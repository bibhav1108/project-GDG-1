import os
from datetime import datetime
from loguru import logger
from common.config import settings

def setup_logging():
    log_dir = settings.get("logging.dir", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"docufill_{datetime.now():%Y%m%d_%H%M%S}.log")
    logger.remove()
    logger.add(
        log_path,
        rotation="1 week",
        retention="4 weeks",
        level=settings.get("logging.level", "INFO"),
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format="{time} | {level} | {message}",
    )
    logger.add(lambda msg: print(msg, end=""))  # mirror to stdout for console runs
    logger.info("Logging initialized at {}", log_path)
    return logger
