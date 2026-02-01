import json
import os
import socket
from typing import Optional

from src.common import config
from src.common.logger import logger

_language_cache = {}
_missing_log_cache = set()  # tránh spam log

LANGUAGE_DIR = config.language_dir


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def load_language_map(lang: str) -> Optional[dict]:
    """
    Load ngôn ngữ từ file 'lang.json' trong thư mục LANGUAGE_DIR.
    Cache vào _language_cache tránh load lại.
    """
    if lang in _language_cache:
        return _language_cache[lang]

    lang_file = os.path.join(LANGUAGE_DIR, lang + '.json')

    if not os.path.exists(lang_file):
        if lang not in _missing_log_cache:
            logger.warn(f"[WARN] Language file for '{lang}' not found ({lang_file}). Fallback to keyword.")
            _missing_log_cache.add(lang)
        _language_cache[lang] = None
        return None

    try:
        with open(lang_file, "r", encoding="utf-8") as f:
            lang_map = json.load(f)
        _language_cache[lang] = lang_map
        return lang_map
    except Exception as e:
        logger.error(f"[ERROR] Failed to load language file '{lang_file}': {e}")
        _language_cache[lang] = None
        return None
