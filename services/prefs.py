import json
import os
import logging
from typing import Dict

from config import PREFS_FILE

logger = logging.getLogger(__name__)

def load_prefs() -> Dict[str, Dict]:
    if not os.path.exists(PREFS_FILE):
        return {}
    try:
        with open(PREFS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Ошибка при загрузке prefs: %s", e)
        return {}


def save_prefs(prefs: Dict[str, Dict]) -> None:
    try:
        with open(PREFS_FILE, "w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("Ошибка при сохранении prefs: %s", e)


def set_user_pref(user_id: int, key: str, value: str) -> None:
    prefs = load_prefs()
    user_key = str(user_id)
    prefs.setdefault(user_key, {})[key] = value
    save_prefs(prefs)


def get_user_prefs(user_id: int) -> Dict[str, str]:
    prefs = load_prefs()
    return prefs.get(str(user_id), {})
