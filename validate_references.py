#!/usr/bin/env python3
"""
Проверка: ссылки на номера квартир в elevenlabs_rag/*.md существуют в quarters/*.md
Выход с кодом 1, если найдены несоответствия.
"""

import re
import sys
from pathlib import Path
from typing import Set

ROOT = Path(__file__).resolve().parent
QUARTERS = ROOT / "quarters"
RAG = ROOT / "elevenlabs_rag"


def collect_all_numbers_from_quarters() -> Set[str]:
    numbers: Set[str] = set()
    for md in QUARTERS.glob("*.md"):
        text = md.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"№+\s*(\d+)", text):
            numbers.add(m.group(1))
    return numbers


def collect_numbers_from_rag() -> Set[str]:
    numbers: Set[str] = set()
    for md in RAG.glob("*.md"):
        text = md.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"№+\s*(\d+)", text):
            numbers.add(m.group(1))
    return numbers


def main() -> int:
    quarter_nums = collect_all_numbers_from_quarters()
    rag_nums = collect_numbers_from_rag()
    missing = sorted(n for n in rag_nums if n not in quarter_nums)
    if missing:
        print("❌ Не найдены номера квартир, упомянутые в RAG-файлах, отсутствующие в quarters:")
        print(", ".join(missing))
        return 1
    print("✅ Все упоминания номеров квартир соответствуют данным quarters")
    return 0


if __name__ == "__main__":
    sys.exit(main())


