import os
import logging
from src.common import config
from logging.handlers import RotatingFileHandler
import sys

log_dir = config.log_dir
log_file = os.path.join(log_dir, "app")
max_size = 5 * 1024 * 1024
backup_count = 5

os.makedirs(log_dir, exist_ok=True)

# Create logger
logger = logging.getLogger("GlobalLogger")
logger.setLevel(logging.DEBUG)

# Formatter
log_format = logging.Formatter(
    "%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Console handler (safe check: only add if stdout is available)
if sys.stdout:
    try:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
    except Exception:
        pass  # In case sys.stdout behaves oddly in frozen GUI apps

# File handler
file_handler = RotatingFileHandler(f"{log_file}.log", maxBytes=max_size, backupCount=backup_count, encoding='utf-8')
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
