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
        languages = ", ".join((data.get("languages") or {}).values()) or "—"
        currencies = ", ".join(
            f"{v.get('name')} ({k})" for k, v in (data.get("currencies") or {}).items()
        ) or "—"
        flag = data.get("flags", {}).get("png", "")

        return (
            f"{name}\n"
            f"• Столица: {capital}\n"
            f"• Регион: {region} / {subregion}\n"
            f"• Население: {population:_}\n"
            f"• Площадь: {area:_} км²\n"
            f"• Валюты: {currencies}\n"
            f"• Языки: {languages}\n"
            f"Флаг: {flag}"
        )
    except Exception as e:
        logger.error("Ошибка форматирования страны: %s", e)
        return "Ошибка при форматировании данных."


def build_top_df(all_countries: List[Dict]) -> pd.DataFrame:
    rows = []
    for c in all_countries:
        try:
            rows.append({
                "name": c.get("name", {}).get("common", "—"),
                "population": int(c.get("population") or 0),
                "area": float(c.get("area") or 0.0),
            })
        except Exception:
            continue
    return pd.DataFrame(rows)