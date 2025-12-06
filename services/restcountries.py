import logging
from typing import Optional, List, Dict
import requests  # <-- ВАЖНО: Нужен для API-запросов
import json
import os

logger = logging.getLogger(__name__)

# Файлы данных
LOCAL_DATA_FILE = "countries_data.json"
BUILTIN_DATA_FILE = "builtin_countries.json"


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
    """Загружает полный список стран для топа через REST Countries API."""
    url = "https://restcountries.com/v3.1/all"
    headers = {
        'User-Agent': 'TelegramBot/1.0',
        'Accept': 'application/json'
    }

    try:
        logger.info("Попытка загрузить полный список стран через API...")
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


# --- ГЛАВНАЯ ФУНКЦИЯ ПОИСКА СТРАНЫ ---

def fetch_country_by_name(name: str) -> Optional[Dict]:
    """
    Получить информацию о стране по имени:
    1. Поиск в локальном кэше.
    2. Поиск во встроенном резерве.
    3. Поиск через API (только если не найдено локально).
    """
    try:
        if not name or not name.strip():
            logger.warning("Пустое название страны")
            return None

        name = name.strip()

        # 1. Поиск в локальных данных (кэш и резерв)
        all_countries = load_local_countries()
        if not all_countries:
            all_countries = get_builtin_countries()

        # Ищем в локальных/встроенных данных
        if all_countries:
            for country in all_countries:
                country_name = country.get("name", {}).get("common", "").lower()
                if country_name == name.lower():
                    logger.info(f"Страна '{name}' найдена в локальных данных")
                    return country

        # 2. Если не найдено локально, обращаемся к API (НОВОЕ ИЗМЕНЕНИЕ)
        logger.info(f"Страна '{name}' не найдена локально. Поиск через API...")
        url = f"https://restcountries.com/v3.1/name/{name}?fullText=true"
        headers = {'User-Agent': 'TelegramBot/1.0', 'Accept': 'application/json'}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    logger.info(f"Страна '{name}' найдена через API.")
                    # Возвращаем первый результат
                    return data[0]

            # Если статус 404 (Not Found) или другой
            logger.warning(f"API не нашел страну '{name}'. Статус: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети при поиске '{name}' через API: {e}")

        logger.warning(f"Страна '{name}' не найдена ни в одном источнике.")
        return None

    except Exception as e:
        logger.error(f"Критическая ошибка в fetch_country_by_name для '{name}': {e}", exc_info=True)
        return None


# --- ФУНКЦИЯ ДЛЯ ТОПА (ОСТАЛАСЬ БЕЗ ИЗМЕНЕНИЙ) ---

def fetch_all_countries() -> Optional[List[Dict]]:
    """
    Получить список всех стран для топа:
    1. API -> сохраняется в кэш.
    2. Локальный кэш.
    3. Встроенный список.
    """
    logger.info("Получение списка стран для топа...")

    # 1. Сначала пробуем получить данные из API
    api_data = fetch_all_countries_from_api()
    if api_data:
        save_local_countries(api_data)
        logger.info("Используем полный список, полученный из API.")
        return api_data

    # 2. Если API недоступен, пробуем загрузить из локального файла (кэша)
    logger.warning("API недоступен. Пробуем использовать локальный кэш...")
    local_data = load_local_countries()
    if local_data:
        logger.info(f"Используем локальный кэш: {len(local_data)} стран")
        return local_data

    # 3. Если нет ни API, ни кэша, используем встроенный резерв
    logger.error("Локальный кэш также недоступен. Используем встроенный резервный список.")
    builtin_countries = get_builtin_countries()

    if builtin_countries:
        save_local_countries(builtin_countries)

    logger.info(f"Используем встроенный резерв: {len(builtin_countries)} стран")
    return builtin_countries