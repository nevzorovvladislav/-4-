import logging
import pandas as pd
from typing import Dict, List

logger = logging.getLogger(__name__)


def format_country_info(data: Dict) -> str:
    """Форматирует данные страны в читаемый вид для Telegram."""
    try:
        name = data.get("name", {}).get("common", "—")
        capital = ", ".join(data.get("capital", ["—"]))
        population = data.get("population", "—")
        area = data.get("area", "—")
        region = data.get("region", "—")
        subregion = data.get("subregion", "—")

        # Языки
        languages_dict = data.get("languages") or {}
        languages = ", ".join(languages_dict.values()) if languages_dict else "—"

        # Валюты
        currencies_dict = data.get("currencies") or {}
        currencies = ", ".join(
            f"{v.get('name')} ({k})" for k, v in currencies_dict.items()
        ) if currencies_dict else "—"

        # Флаг
        flag = data.get("flags", {}).get("png", "")

        # Форматируем числа (разделяем нижним подчеркиванием для читаемости)
        pop_str = f"{population:,}".replace(",", "_") if population != "—" else "—"
        area_str = f"{area:,}".replace(",", "_") if area != "—" else "—"

        return (
            f"{name}\n\n"
            f"🏛️ Столица: {capital}\n"
            f"🗺️ Регион: {region} / {subregion}\n"
            f"👥 Население: {pop_str}\n"
            f"📏 Площадь: {area_str} км²\n"
            f"💰 Валюты: {currencies}\n"
            f"🗣️ Языки: {languages}\n"
            f"🏳️ Флаг: {flag}"
        )
    except Exception as e:
        logger.error(f"Ошибка форматирования страны: {e}")
        return "❌ Ошибка при получении данных о стране."


def build_top_df(all_countries: List[Dict]) -> pd.DataFrame:
    """Создает DataFrame из списка стран для расчета топа."""
    rows = []
    if not all_countries:
        return pd.DataFrame(columns=["name", "population", "area"])

    for c in all_countries:
        try:
            # Получаем имя страны
            name_data = c.get("name", {})
            name = name_data.get("common", "Unknown") if isinstance(name_data, dict) else str(name_data)

            # Получаем и проверяем население
            population = c.get("population")
            try:
                population = int(population) if population is not None else 0
            except (ValueError, TypeError):
                population = 0

            # Получаем и проверяем площадь
            area = c.get("area")
            try:
                area = float(area) if area is not None else 0.0
            except (ValueError, TypeError):
                area = 0.0

            rows.append({
                "name": name,
                "population": population,
                "area": area,
            })
        except Exception as e:
            logger.warning(f"Ошибка при обработке страны для DataFrame: {e}")
            continue

    if not rows:
        return pd.DataFrame(columns=["name", "population", "area"])

    return pd.DataFrame(rows)