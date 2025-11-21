#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генерация отдельного файла квартала "02 Эмиратс"
Собирает все объекты "Эмиратс Волна 7с/8с" из квартала 9 Южная Америка
и сохраняет markdown в quarters/02-emirats.md
"""

import os
import re
from collections import defaultdict
from typing import Dict, List

from bir_data_parser import BirDataParser


def extract_emirats_label(location_text: str) -> str:
    """Возвращает ярлык дома из текста местоположения: 'Эмиратс Волна 8с' или 'Эмиратс Волна 7с'."""
    if not location_text:
        return "Эмиратс"
    # Ищем шаблон вида 'Эмиратс Волна 8с' или 'Эмиратс Волна 7с'
    m = re.search(r"Эмиратс\s*Волна\s*([0-9]+с)", location_text)
    if m:
        return f"Эмиратс Волна {m.group(1)}"
    # fallback: просто 'Эмиратс'
    return "Эмиратс"


def build_emirats_houses(parser: BirDataParser) -> Dict[str, List[dict]]:
    """Формирует словарь домов Эмиратс -> список квартир (структурированных)."""
    emirats_houses: Dict[str, List[dict]] = defaultdict(list)

    # Берём только квартал 9 Южная Америка и фильтруем квартиры по 'Эмиратс Волна'
    quarter_name = "9 Южная Америка"
    if quarter_name not in parser.quarters:
        return emirats_houses

    for house_number, apartments in parser.quarters[quarter_name].items():
        for apt in apartments:
            location = apt.get("location", "") or ""
            house_name = apt.get("house_name", "") or ""
            address = apt.get("address", "") or ""

            if ("Эмиратс Волна" in location) or ("Эмиратс Волна" in house_name) or ("Эмиратс Волна" in address):
                # Клонируем запись и выставляем удобное имя дома как ключ
                apt_copy = dict(apt)
                label = extract_emirats_label(location) or "Эмиратс"
                # Для красоты заголовков дома используем полный ярлык, а не цифру
                apt_copy["house_number"] = label
                emirats_houses[label].append(apt_copy)

    return emirats_houses


def generate_emirats_markdown(parser: BirDataParser, emirats_houses: Dict[str, List[dict]]) -> str:
    """Генерирует markdown контент для квартала '02 Эмиратс'."""
    quarter_display = "02 Эмиратс"

    # Считаем агрегаты
    total_objects = sum(len(apts) for apts in emirats_houses.values())
    unique_types = set()
    for apts in emirats_houses.values():
        for apt in apts:
            if apt.get("type"):
                unique_types.add(apt["type"])

    md = []
    md.append(f"# 🏘️ Квартал — {quarter_display}\n")
    md.append("## 📍 Общая информация\n")
    md.append(f"**Квартал:** {quarter_display}\n")
    md.append("**Город:** Минск\n")
    md.append("**Район:** Мир\n")
    md.append(f"**Количество домов:** {len(emirats_houses)}\n")
    md.append(f"**Количество объектов:** {total_objects}\n")
    if unique_types:
        md.append(f"**Типы недвижимости:** {', '.join(sorted(unique_types))}\n")
    md.append("\n---\n\n")

    # Блоки по домам
    # Стабильный порядок: сначала 7с, потом 8с, затем прочее (если появится)
    def emirats_sort_key(k: str) -> tuple:
        m = re.search(r"(\d+)с", k)
        num = int(m.group(1)) if m else 999
        return (num, k)

    for house_label in sorted(emirats_houses.keys(), key=emirats_sort_key):
        apts = emirats_houses[house_label]
        md.append(f"## 🏠 Дом {house_label}\n\n")

        # Лёгкая статистика по дому
        prices = [apt["price_metr"] for apt in apts if apt.get("price_metr", 0) > 0]
        squares = [apt["square"] for apt in apts if apt.get("square", 0) > 0]
        costs = [apt["price_full"] for apt in apts if apt.get("price_full", 0) > 0]

        md.append("### 📊 Статистика дома\n")
        md.append(f"**Количество апартаментов:** {len(apts)}\n")
        if squares:
            md.append(f"**Диапазон площадей:** {min(squares):.1f} - {max(squares):.1f} м²\n")
        if prices:
            md.append(f"**Средняя цена за м²:** {sum(prices)/len(prices):.0f} евро\n")
        if costs:
            md.append(f"**Средняя стоимость:** {sum(costs)/len(costs):.0f} евро\n")
        md.append("\n---\n\n")

        # Группируем по этажам
        floors: Dict[int, List[dict]] = defaultdict(list)
        for apt in apts:
            floors[apt.get("floor", 0)].append(apt)

        for floor_num in sorted(floors.keys()):
            md.append(f"## 🏢 Этаж {floor_num}\n\n")
            for apt in floors[floor_num]:
                md.append(parser.generate_apartment_markdown(apt))
            md.append("\n")

    # Общая аналитика по кварталу
    all_prices, all_squares, all_costs = [], [], []
    for apts in emirats_houses.values():
        for apt in apts:
            if apt.get("price_metr", 0) > 0:
                all_prices.append(apt["price_metr"])
            if apt.get("square", 0) > 0:
                all_squares.append(apt["square"])
            if apt.get("price_full", 0) > 0:
                all_costs.append(apt["price_full"])

    if all_prices or all_squares or all_costs:
        md.append(parser.generate_quarter_analytics(all_prices, all_squares, all_costs))

    return "".join(md)


def main():
    print("🏘️ Формирование квартала '02 Эмиратс'")
    parser = BirDataParser()
    if not parser.fetch_data():
        print("❌ Не удалось загрузить данные")
        return
    parser.parse_data()

    emirats_houses = build_emirats_houses(parser)
    total = sum(len(v) for v in emirats_houses.values())
    if total == 0:
        print("⚠️ Объекты Эмиратс не найдены в текущих данных")
        return

    markdown = generate_emirats_markdown(parser, emirats_houses)

    out_dir = "quarters"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "02-emirats.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"✅ Создан файл: {out_path} ({total} объектов)")


if __name__ == "__main__":
    main()



