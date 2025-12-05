import logging
from typing import Optional, List, Dict
import json
import os

logger = logging.getLogger(__name__)

# Файл для локальных данных
LOCAL_DATA_FILE = "countries_data.json"
# Файл со встроенными данными
BUILTIN_DATA_FILE = "builtin_countries.json"

def get_builtin_countries():
    """Загружает встроенные страны из JSON файла."""
    try:
        # Если файл существует в текущей директории
        if os.path.exists(BUILTIN_DATA_FILE):
            with open(BUILTIN_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Альтернативно, файл может быть рядом с модулем
            module_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(module_dir, BUILTIN_DATA_FILE)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Файл {BUILTIN_DATA_FILE} не найден")
                return []
    except Exception as e:
        logger.error(f"Ошибка загрузки встроенных данных: {e}")
        return []

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
    """Получить информацию о стране по имени (только из локального/встроенного списка)."""
    try:
        if not name or not name.strip():
            logger.warning("Пустое название страны")
            return None

        name = name.strip()
        all_countries = load_local_countries()

        # Если локальный кэш не загружен, используем встроенный список
        if not all_countries:
            all_countries = get_builtin_countries()

        # Поиск в доступных данных
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
    Получить список всех стран для топа, используя только локальные данные.
    """
    logger.info("Получение списка стран для топа (Локальный режим)...")

    # 1. Сначала пробуем загрузить из локального кэша
    local_data = load_local_countries()
    if local_data and len(local_data) >= 50:
        logger.info(f"Используем локальный кэш: {len(local_data)} стран")
        return local_data

    # 2. Если кэш не полон или пуст, используем встроенные данные
    logger.info("Локальный кэш не полон/пуст. Используем встроенный список.")
    builtin_countries = get_builtin_countries()

    # Сохраняем встроенные данные в локальный файл, чтобы ускорить следующий запуск
    if builtin_countries:
        save_local_countries(builtin_countries)

    logger.info(f"Используем встроенный резервный список: {len(builtin_countries)} стран")
    return builtin_countries