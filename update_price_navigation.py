#!/usr/bin/env python3
"""
Генерация авто-блоков в RAG-файлах (price navigation) на основе pricing_index.json
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

ROOT = Path(__file__).resolve().parent
RAG_DIR = ROOT / "elevenlabs_rag"


def load_index(index_path: Path) -> Dict[str, Any]:
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_euro(value: float) -> str:
    return f"{value:,.0f}€".replace(",", " ")


def render_quarter_min_line(quarter_md: str, index: Dict[str, Any]) -> str:
    qmin = index.get("quarters_min_prices", {}).get(quarter_md)
    if not qmin:
        return f"- {quarter_md}: —"
    return f"- {quarter_md}: от {format_euro(qmin['min_price'])}"


def top_n_apartments_for_quarter(index: Dict[str, Any], quarter_md: str, n: int = 3) -> List[Dict[str, Any]]:
    # Найдем все квартиры данного квартала через budget_categories
    result: List[Dict[str, Any]] = []
    for cat in index.get("budget_categories", {}).values():
        for apt in cat.get("apartments", []):
            if apt.get("quarter") == quarter_md:
                result.append(apt)
    result.sort(key=lambda x: x.get("price", 10**18))
    return result[:n]


def render_apartment_line(apt: Dict[str, Any]) -> str:
    number = apt.get("number", "?")
    area = apt.get("area", "?")
    price = apt.get("price")
    price_str = format_euro(price) if isinstance(price, (int, float)) else "—"
    return f"- №{number}: {area} м², {price_str}"


def replace_auto_block(content: str, section: str, new_block: str) -> str:
    start = f"<!-- AUTO:START section={section} -->"
    end = f"<!-- AUTO:END section={section} -->"
    pattern = re.compile(re.escape(start) + r"[\s\S]*?" + re.escape(end), re.MULTILINE)
    replacement = start + "\n" + new_block.strip() + "\n" + end
    if pattern.search(content):
        return pattern.sub(replacement, content)
    else:
        # Если маркеров нет — добавим в конец файла
        return content.rstrip() + "\n\n" + replacement + "\n"


def update_00_price_navigation(index: Dict[str, Any], path: Path):
    content = path.read_text(encoding="utf-8")
    # Секции: ultra, budget, affordable, table-min
    # 1) ultra: только 21 квартал (если есть данные)
    ultra_lines: List[str] = []
    ultra_q = "21-Zapadnyy.md"
    ultra_line = render_quarter_min_line(ultra_q, index)
    if "—" not in ultra_line:
        ultra_lines.append(ultra_line)
    ultra_block = "\n".join(ultra_lines) if ultra_lines else "(нет актуальных предложений)"
    content = replace_auto_block(content, "ultra", ultra_block)

    # 2) budget priority: 7, 21, 30
    budget_quarters = ["7-Sredizemnomorskiy.md", "21-Zapadnyy.md", "30-Severnaya-Amerika.md", "19-Yuzhnaya-Evropa.md", "26-Afrika.md"]
    budget_block = "\n".join(render_quarter_min_line(q, index) for q in budget_quarters if index.get("quarters_min_prices", {}).get(q))
    content = replace_auto_block(content, "budget-mins", budget_block or "(нет актуальных предложений)")

    # 3) table-min: таблица кварталов с мин. ценой (поддерживаем существующий список)
    table_lines: List[str] = []
    for quarter_md, meta in sorted(index.get("quarters_min_prices", {}).items()):
        table_lines.append(f"| {quarter_md} | от {format_euro(meta['min_price'])} |")
    content = replace_auto_block(content, "table-min", "\n".join(table_lines) or "(нет данных)")

    path.write_text(content, encoding="utf-8")


def update_01_budget_apartments(index: Dict[str, Any], path: Path):
    content = path.read_text(encoding="utf-8")
    # Сформируем блоки для 7, 21, 30
    blocks = []
    for q in ["7-Sredizemnomorskiy.md", "21-Zapadnyy.md", "30-Severnaya-Amerika.md"]:
        apts = top_n_apartments_for_quarter(index, q, 3)
        if not apts:
            continue
        mins = index.get("quarters_min_prices", {}).get(q, {}).get("min_price")
        header = f"### {q.replace('.md', '')} — от {format_euro(mins)}" if mins else f"### {q.replace('.md', '')}"
        lines = [render_apartment_line(a) for a in apts]
        blocks.append("\n".join([header] + lines))
    block_text = "\n\n".join(blocks) if blocks else "(нет актуальных предложений)"
    content = replace_auto_block(content, "budget-top", block_text)
    path.write_text(content, encoding="utf-8")


def update_10_budget_apartments(index: Dict[str, Any], path: Path):
    # Аналогично, но можно расширить список кварталов
    content = path.read_text(encoding="utf-8")
    quarters = ["19-Yuzhnaya-Evropa.md", "26-Afrika.md", "25-Aziya.md", "23-Evraziya.md"]
    blocks = []
    for q in quarters:
        apts = top_n_apartments_for_quarter(index, q, 3)
        if not apts:
            continue
        mins = index.get("quarters_min_prices", {}).get(q, {}).get("min_price")
        header = f"### {q.replace('.md', '')} — от {format_euro(mins)}" if mins else f"### {q.replace('.md', '')}"
        lines = [render_apartment_line(a) for a in apts]
        blocks.append("\n".join([header] + lines))
    block_text = "\n\n".join(blocks) if blocks else "(нет актуальных предложений)"
    content = replace_auto_block(content, "affordable-top", block_text)
    path.write_text(content, encoding="utf-8")


def main():
    index_path = ROOT / "pricing_index.json"
    if not index_path.exists():
        raise SystemExit("pricing_index.json не найден. Сначала выполните build_pricing_index.py")
    index = load_index(index_path)

    update_00_price_navigation(index, RAG_DIR / "00-price-navigation.md")
    update_01_budget_apartments(index, RAG_DIR / "01-budget-apartments.md")
    update_10_budget_apartments(index, RAG_DIR / "10-budget-apartments.md")
    print("✅ Обновлены авто-блоки в RAG-файлах")


if __name__ == "__main__":
    main()


