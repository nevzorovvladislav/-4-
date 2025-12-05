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
        logger.info("Запрос всех стран из API...")

        # Добавляем User-Agent и параметры для стабильности
        headers = {
            'User-Agent': 'CountryBot/1.0'
        }

        # Пробуем несколько вариантов запроса
        resp = requests.get(RESTCOUNTRIES_ALL_ENDPOINT, timeout=30, headers=headers)
        resp.raise_for_status()

        data = resp.json()

        if isinstance(data, list):
            logger.info(f"Успешно получено {len(data)} стран")
            return data
        else:
            logger.error(f"Ожидался список, получен {type(data)}")
            return None
    except requests.exceptions.Timeout:
        logger.error("Таймаут при запросе всех стран")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Ошибка подключения к API стран")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP ошибка: {e.response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка при запросе всех стран: {e}")
        return None