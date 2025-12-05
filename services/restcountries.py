import logging
from typing import Optional, List, Dict
import requests

from config import RESTCOUNTRIES_NAME_ENDPOINT, RESTCOUNTRIES_ALL_ENDPOINT

logger = logging.getLogger(__name__)

def fetch_country_by_name(name: str) -> Optional[Dict]:
    try:
        resp = requests.get(RESTCOUNTRIES_NAME_ENDPOINT.format(name), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            return data[0]
        return None
    except Exception as e:
        logger.error("Ошибка API при поиске страны '%s': %s", name, e)
        return None


def fetch_all_countries() -> Optional[List[Dict]]:
    try:
        resp = requests.get(RESTCOUNTRIES_ALL_ENDPOINT, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        return None
    except Exception as e:
        logger.error("Ошибка API /all: %s", e)
        return None
