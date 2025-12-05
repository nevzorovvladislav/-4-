import logging
from typing import Optional, List, Dict
import requests
import json
import os

logger = logging.getLogger(__name__)

# Файл для локальных данных, который будет создан в корне проекта
LOCAL_DATA_FILE = "countries_data.json"


def get_builtin_countries():
    """Встроенный набор популярных стран для начального кэша и резерва."""
    return [
        {"name": {"common": "Russia"}, "capital": ["Moscow"], "region": "Europe", "subregion": "Eastern Europe",
         "population": 146599183, "area": 17098246, "languages": {"rus": "Russian"},
         "currencies": {"RUB": {"name": "Russian ruble"}}, "flags": {"png": "https://flagcdn.com/w320/ru.png"}},
        {"name": {"common": "Germany"}, "capital": ["Berlin"], "region": "Europe", "subregion": "Western Europe",
         "population": 83240525, "area": 357022, "languages": {"deu": "German"},
         "currencies": {"EUR": {"name": "Euro"}}, "flags": {"png": "https://flagcdn.com/w320/de.png"}},
        {"name": {"common": "United States"}, "capital": ["Washington, D.C."], "region": "Americas",
         "subregion": "North America", "population": 329484123, "area": 9372610, "languages": {"eng": "English"},
         "currencies": {"USD": {"name": "United States dollar"}}, "flags": {"png": "https://flagcdn.com/w320/us.png"}},
        {"name": {"common": "China"}, "capital": ["Beijing"], "region": "Asia", "subregion": "Eastern Asia",
         "population": 1402112000, "area": 9596961, "languages": {"zho": "Chinese"},
         "currencies": {"CNY": {"name": "Chinese yuan"}}, "flags": {"png": "https://flagcdn.com/w320/cn.png"}},
        {"name": {"common": "India"}, "capital": ["New Delhi"], "region": "Asia", "subregion": "Southern Asia",
         "population": 1393409038, "area": 3287263, "languages": {"eng": "English", "hin": "Hindi"},
         "currencies": {"INR": {"name": "Indian rupee"}}, "flags": {"png": "https://flagcdn.com/w320/in.png"}},
        {"name": {"common": "Brazil"}, "capital": ["Brasília"], "region": "Americas", "subregion": "South America",
         "population": 213993437, "area": 8515767, "languages": {"por": "Portuguese"},
         "currencies": {"BRL": {"name": "Brazilian real"}}, "flags": {"png": "https://flagcdn.com/w320/br.png"}},
        {"name": {"common": "Japan"}, "capital": ["Tokyo"], "region": "Asia", "subregion": "Eastern Asia",
         "population": 125836021, "area": 377930, "languages": {"jpn": "Japanese"},
         "currencies": {"JPY": {"name": "Japanese yen"}}, "flags": {"png": "https://flagcdn.com/w320/jp.png"}},
        {"name": {"common": "France"}, "capital": ["Paris"], "region": "Europe", "subregion": "Western Europe",
         "population": 67391582, "area": 551695, "languages": {"fra": "French"},
         "currencies": {"EUR": {"name": "Euro"}}, "flags": {"png": "https://flagcdn.com/w320/fr.png"}},
        {"name": {"common": "United Kingdom"}, "capital": ["London"], "region": "Europe",
         "subregion": "Northern Europe", "population": 67215293, "area": 242900, "languages": {"eng": "English"},
         "currencies": {"GBP": {"name": "British pound"}}, "flags": {"png": "https://flagcdn.com/w320/gb.png"}},
        {"name": {"common": "Italy"}, "capital": ["Rome"], "region": "Europe", "subregion": "Southern Europe",
         "population": 59554023, "area": 301336, "languages": {"ita": "Italian"},
         "currencies": {"EUR": {"name": "Euro"}}, "flags": {"png": "https://flagcdn.com/w320/it.png"}},
        {"name": {"common": "Canada"}, "capital": ["Ottawa"], "region": "Americas", "subregion": "North America",
         "population": 38005238, "area": 9984670, "languages": {"eng": "English", "fra": "French"},
         "currencies": {"CAD": {"name": "Canadian dollar"}}, "flags": {"png": "https://flagcdn.com/w320/ca.png"}},
        {"name": {"common": "Australia"}, "capital": ["Canberra"], "region": "Oceania",
         "subregion": "Australia and New Zealand", "population": 25687041, "area": 7692024,
         "languages": {"eng": "English"}, "currencies": {"AUD": {"name": "Australian dollar"}},
         "flags": {"png": "https://flagcdn.com/w320/au.png"}},
        {"name": {"common": "Mexico"}, "capital": ["Mexico City"], "region": "Americas", "subregion": "North America",
         "population": 128932753, "area": 1964375, "languages": {"spa": "Spanish"},
         "currencies": {"MXN": {"name": "Mexican peso"}}, "flags": {"png": "https://flagcdn.com/w320/mx.png"}},
        {"name": {"common": "Spain"}, "capital": ["Madrid"], "region": "Europe", "subregion": "Southern Europe",
         "population": 47351567, "area": 505992, "languages": {"spa": "Spanish"},
         "currencies": {"EUR": {"name": "Euro"}}, "flags": {"png": "https://flagcdn.com/w320/es.png"}},
        {"name": {"common": "South Korea"}, "capital": ["Seoul"], "region": "Asia", "subregion": "Eastern Asia",
         "population": 51780579, "area": 100210, "languages": {"kor": "Korean"},
         "currencies": {"KRW": {"name": "South Korean won"}}, "flags": {"png": "https://flagcdn.com/w320/kr.png"}},
        {"name": {"common": "Ukraine"}, "capital": ["Kyiv"], "region": "Europe", "subregion": "Eastern Europe",
         "population": 44134693, "area": 603500, "languages": {"ukr": "Ukrainian"},
         "currencies": {"UAH": {"name": "Ukrainian hryvnia"}}, "flags": {"png": "https://flagcdn.com/w320/ua.png"}},
        {"name": {"common": "Poland"}, "capital": ["Warsaw"], "region": "Europe", "subregion": "Central Europe",
         "population": 37950802, "area": 312679, "languages": {"pol": "Polish"},
         "currencies": {"PLN": {"name": "Polish złoty"}}, "flags": {"png": "https://flagcdn.com/w320/pl.png"}},
        {"name": {"common": "Turkey"}, "capital": ["Ankara"], "region": "Asia", "subregion": "Western Asia",
         "population": 84339067, "area": 783562, "languages": {"tur": "Turkish"},
         "currencies": {"TRY": {"name": "Turkish lira"}}, "flags": {"png": "https://flagcdn.com/w320/tr.png"}},
        {"name": {"common": "Egypt"}, "capital": ["Cairo"], "region": "Africa", "subregion": "Northern Africa",
         "population": 102334404, "area": 1002450, "languages": {"ara": "Arabic"},
         "currencies": {"EGP": {"name": "Egyptian pound"}}, "flags": {"png": "https://flagcdn.com/w320/eg.png"}},
        {"name": {"common": "Vietnam"}, "capital": ["Hanoi"], "region": "Asia", "subregion": "South-Eastern Asia",
         "population": 97338579, "area": 331212, "languages": {"vie": "Vietnamese"},
         "currencies": {"VND": {"name": "Vietnamese đồng"}}, "flags": {"png": "https://flagcdn.com/w320/vn.png"}},
    ]


def load_local_countries():
    """Загружает страны из локального файла."""
    if os.path.exists(LOCAL_DATA_FILE):
        try:
            with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    logger.info(f"Загружено {len(data)} стран из локального файла")
                    return data
        except Exception as e:
            logger.error(f"Ошибка загрузки локальных данных: {e}")
    return None


def save_local_countries(countries):
    """Сохраняет страны в локальный файл."""
    try:
        with open(LOCAL_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(countries, f, ensure_ascii=False, indent=2)
        logger.info(f"Сохранено {len(countries)} стран в локальный файл")
    except Exception as e:
        logger.error(f"Ошибка сохранения локальных данных: {e}")


def fetch_country_by_name(name: str) -> Optional[Dict]:
    """Получить информацию о стране по имени (сначала локально, затем через API, затем встроенно)."""
    try:
        if not name or not name.strip():
            logger.warning("Пустое название страны")
            return None

        name = name.strip()

        # 1. Проверяем локальные данные (если есть)
        local_data = load_local_countries()
        if local_data:
            for country in local_data:
                country_name = country.get("name", {}).get("common", "").lower()
                if country_name == name.lower():
                    logger.info(f"Страна '{name}' найдена в локальных данных")
                    return country

        # 2. Пробуем через API (если не нашли локально)
        logger.info(f"Поиск '{name}' через API...")
        url = f"https://restcountries.com/v3.1/name/{name}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            logger.info(f"API статус для '{name}': {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    logger.info(f"Страна '{name}' найдена через API")
                    return data[0]
                else:
                    logger.warning(f"Для '{name}' получен пустой ответ от API")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети при запросе '{name}': {e}")
        except Exception as e:
            logger.error(f"Ошибка при обработке ответа для '{name}': {e}")

        # 3. Ищем во встроенных данных (резервный вариант)
        logger.info(f"Поиск '{name}' во встроенных данных...")
        builtin_countries = get_builtin_countries()
        for country in builtin_countries:
            country_name = country.get("name", {}).get("common", "").lower()
            if country_name == name.lower():
                logger.info(f"Страна '{name}' найдена во встроенных данных")
                return country

        logger.warning(f"Страна '{name}' не найдена ни в одном источнике")
        return None

    except Exception as e:
        logger.error(f"Критическая ошибка в fetch_country_by_name для '{name}': {e}", exc_info=True)
        return None


def fetch_all_countries() -> Optional[List[Dict]]:
    """Получить список всех стран: сначала локально, затем создаем из встроенных данных."""
    logger.info("Получение списка стран...")

    # 1. Сначала пробуем загрузить из локального файла
    local_data = load_local_countries()
    if local_data:
        logger.info(f"Используем локальные данные: {len(local_data)} стран")
        return local_data

    # 2. Если локального файла нет, создаем его из встроенных данных
    logger.info("Создаем локальный файл с встроенными данными")
    builtin_countries = get_builtin_countries()
    save_local_countries(builtin_countries)

    logger.info(f"Используем встроенные данные: {len(builtin_countries)} стран")
    return builtin_countries