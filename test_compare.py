import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.restcountries import fetch_country_by_name

print("Тестирование функции сравнения стран...")

# Тестируем поиск отдельных стран
test_countries = ["Russia", "Germany", "France", "Japan", "China"]

for country in test_countries:
    print(f"\nПоиск страны: {country}")
    result = fetch_country_by_name(country)
    if result:
        name = result.get("name", {}).get("common", "Unknown")
        print(f"✅ Найдено: {name}")
        print(f"   Население: {result.get('population', 0):,}")
        print(f"   Площадь: {result.get('area', 0):,}")
    else:
        print(f"❌ Не найдено: {country}")

print("\n" + "=" * 50)
print("Тестирование сравнения Russia | Germany...")

russia = fetch_country_by_name("Russia")
germany = fetch_country_by_name("Germany")

if russia and germany:
    print("✅ Обе страны найдены!")
    print(f"Russia: {russia.get('name', {}).get('common')}")
    print(f"Germany: {germany.get('name', {}).get('common')}")

    pop1 = russia.get("population", 0)
    pop2 = germany.get("population", 0)
    area1 = russia.get("area", 0)
    area2 = germany.get("area", 0)

    print(f"\nСравнение:")
    print(f"Население: {pop1:,} vs {pop2:,}")
    print(f"Площадь: {area1:,} км² vs {area2:,} км²")
else:
    print("❌ Одна или обе страны не найдены")
    if not russia:
        print("Russia не найдена")
    if not germany:
        print("Germany не найдена")

print("\nТест завершен!")