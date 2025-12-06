import logging
from typing import Optional, List, Dict
import requests  # <-- ВОЗВРАЩАЕМ ИМПОРТ ДЛЯ РАБОТЫ С API
import json
import os

logger = logging.getLogger(__name__)

# Файлы данных
LOCAL_DATA_FILE = "countries_data.json"
BUILTIN_DATA_FILE = "builtin_countries.json"  # Предполагаем, что этот файл существует


# --- Функции ввода/вывода данных ---

def get_builtin_countries():
    """Загружает встроенные страны из JSON файла (резерв)."""
    try:
        if os.path.exists(BUILTIN_DATA_FILE):
            with open(BUILTIN_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(module_dir, BUILTIN_DATA_FILE)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Файл {BUILTIN_DATA_FILE} не найден. Возвращаем пустой список.")
                return []
    except Exception as e:
        logger.error(f"Ошибка загрузки встроенных данных: {e}")
        return []


def load_local_countries():
    """Загружает страны из локального файла (кэш)."""
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


# --- ФУНКЦИЯ ДЛЯ РАБОТЫ С API ---

def fetch_all_countries_from_api() -> Optional[List[Dict]]:
    """Загружает полный список стран со всеми данными через REST Countries API."""
    # Используем 'v3.1/all' для получения полного списка
    url = "https://restcountries.com/v3.1/all"
    headers = {
        'User-Agent': 'TelegramBot/1.0',
        'Accept': 'application/json'
    }

    try:
        logger.info("Попытка загрузить полный список стран через API...")
        # Увеличиваем таймаут на случай медленного ответа
        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                logger.info(f"Успешно загружено {len(data)} стран через API.")
                return data
            else:
                logger.warning("API вернул пустой или некорректный список стран.")
                return None
        else:
            logger.error(f"Ошибка API при загрузке всех стран. Статус: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети при загрузке всех стран (API недоступен): {e}")
        return None


# --- ГЛАВНАЯ ФУНКЦИЯ ПОЛУЧЕНИЯ ДАННЫХ ---

def fetch_country_by_name(name: str) -> Optional[Dict]:
    """Получить информацию о стране по имени (используется только локальный/встроенный список)."""
    # Логика поиска по имени остается локальной, чтобы не вызывать API для каждой команды /info.
    try:
        if not name or not name.strip():
            logger.warning("Пустое название страны")
            return None

        name = name.strip()
        all_countries = load_local_countries()

        if not all_countries:
            all_countries = get_builtin_countries()

        if all_countries:
            for country in all_countries:
                country_name = country.get("name", {}).get("common", "").lower()
                if country_name == name.lower():
                    logger.info(f"Страна '{name}' найдена в локальных данных")
                    return country

        logger.warning(f"Страна '{name}' не найдена в локальном списке")
        return None

    except Exception as e:
        logger.error(f"Критическая ошибка в fetch_country_by_name для '{name}': {e}", exc_info=True)
        return None


def fetch_all_countries() -> Optional[List[Dict]]:
    """
    Получить список всех стран для топа:
    1. API (если успешно) -> сохраняется в кэш.
    2. Локальный кэш (если API не сработал).
    3. Встроенный список (если нет ни API, ни кэша).
    """
    logger.info("Получение списка стран для топа...")

    # 1. Сначала пробуем получить данные из API (приоритет свежим данным)
    api_data = fetch_all_countries_from_api()
    if api_data:
        # Успешно, сохраняем в локальный файл для кэша
        save_local_countries(api_data)
        logger.info("Используем полный список, полученный из API.")
        return api_data

    # 2. Если API недоступен, пробуем загрузить из локального файла (кэша)
    logger.warning("API недоступен. Пробуем использовать локальный кэш...")
    local_data = load_local_countries()
    if local_data and len(local_data) >= 50:  # Используем кэш, если он достаточно полон
        logger.info(f"Используем локальный кэш: {len(local_data)} стран")
        return local_data

    # 3. Если нет ни API, ни кэша, используем встроенный резерв
    logger.error("Локальный кэш также недоступен/неполон. Используем встроенный резервный список.")
    builtin_countries = get_builtin_countries()

    # Сохраняем встроенные данные в локальный файл (для кэширования резерва)
    if builtin_countries:
        save_local_countries(builtin_countries)

    logger.info(f"Используем встроенный резерв: {len(builtin_countries)} стран")
    return builtin_countries