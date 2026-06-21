import logging
from logging.handlers import RotatingFileHandler
from src.config import settings

LOG_FILE = "etl_raptor.log"

formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

handler = RotatingFileHandler(LOG_FILE, maxBytes=5_242_880, backupCount=3)
handler.setFormatter(formatter)

logger = logging.getLogger("etl_raptor")
logger.setLevel(settings.log_level)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())
