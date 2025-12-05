import logging
import pandas as pd
from typing import Dict, List

logger = logging.getLogger(__name__)


def format_country_info(data: Dict) -> str:
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

        # Эмодзи для регионов
        region_emojis = {
            "Africa": "🌍",
            "Americas": "🌎",
            "Asia": "🌏",
            "Europe": "🇪🇺",
            "Oceania": "🌊"
        }
        region_emoji = region_emojis.get(region, "📍")

        # УБИРАЕМ ВСЕ ЗВЕЗДОЧКИ И MARKDOWN РАЗМЕТКУ
        return (
            f"{name} {region_emoji}\n\n"
            f"🏛️ Столица: {capital}\n"
            f"🗺️ Регион: {region} / {subregion}\n"
            f"👥 Население: {population:_}\n"
            f"📏 Площадь: {area:_} км²\n"
            f"💰 Валюты: {currencies}\n"
            f"🗣️ Языки: {languages}\n"
            f"🏳️ Флаг: {flag}"
        )
    except Exception as e:
        logger.error("Ошибка форматирования страны: %s", e)
        return "❌ Ошибка при получении данных о стране."


def build_top_df(all_countries: List[Dict]) -> pd.DataFrame:
    rows = []
    if not all_countries:
        return pd.DataFrame(columns=["name", "population", "area"])

    for c in all_countries:
        try:
            rows.append({
                "name": c.get("name", {}).get("common", "—"),
                "population": int(c.get("population") or 0),
                "area": float(c.get("area") or 0.0),
            })
        except Exception:
            continue

    if not rows:
        return pd.DataFrame(columns=["name", "population", "area"])

    return pd.DataFrame(rows)