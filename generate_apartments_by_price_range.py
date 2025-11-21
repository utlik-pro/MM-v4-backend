#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генерация JSON-файла с подборкой квартир по диапазонам цены (EUR).

Источник данных: https://bir.by/ai/json_ai.php

Группировка диапазонов:
- 50,000–60,000
- 60,000–70,000
- 70,000–80,000
- 80,000–90,000
- 100,000–120,000
- 120,000–150,000
- 150,000–200,000
- 200,000–232,000

В каждом диапазоне выбираются до 3 самых дешевых квартир.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests


API_URL = "https://bir.by/ai/json_ai.php"
OUTPUT_PATH = "apartments_by_price_ranges.json"


PriceRange = Tuple[int, int, str]


PRICE_RANGES: List[PriceRange] = [
    (0, 50_000, "до 50 000 €"),
    (50_000, 60_000, "50 000–60 000 €"),
    (60_000, 70_000, "60 000–70 000 €"),
    (70_000, 80_000, "70 000–80 000 €"),
    (80_000, 90_000, "80 000–90 000 €"),
    (100_000, 120_000, "100 000–120 000 €"),
    (120_000, 150_000, "120 000–150 000 €"),
    (150_000, 200_000, "150 000–200 000 €"),
    (200_000, 232_000, "200 000–232 000 €"),
]


def safe_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        s = str(value)
        # keep digits and dot only
        cleaned = "".join(ch for ch in s if (ch.isdigit() or ch in ".-"))
        return float(cleaned) if cleaned else 0.0
    except Exception:
        return 0.0


def decode_unicode(value: Optional[str]) -> str:
    if not value:
        return ""
    try:
        # If already normal text (no leading escape) just return
        if not value.startswith("\\u"):
            return value
        return value.encode("utf-8").decode("unicode_escape")
    except Exception:
        return value


def normalize_apartment(item_id: str, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Normalize one API item into the target structure. Supports 'Квартира' и 'Апартаменты'."""
    raw_type = decode_unicode(raw.get("type", "")).strip()
    item_type_lc = raw_type.lower()
    # поддерживаем Квартира и любые *апартаменты* (в т.ч. Бизнес-апартаменты)
    if "квартир" in item_type_lc:
        unit_type_norm = "Квартира"
    elif "апартам" in item_type_lc:
        unit_type_norm = "Апартаменты"
    else:
        return None

    # Raw fields
    apartment_label = decode_unicode(raw.get("Apartment", ""))
    unit_number: Optional[str] = None
    # Try to extract trailing number from labels like "Квартира №3" or "Квартира 3"
    if apartment_label:
        import re
        m = re.search(r"№?\s*(\d+)$", apartment_label)
        if m:
            unit_number = m.group(1)

    quarter = decode_unicode(raw.get("Quarter", ""))
    status = decode_unicode(raw.get("Status", ""))
    address = decode_unicode(raw.get("Address", ""))
    location = decode_unicode(raw.get("Location", ""))
    house_number = decode_unicode(raw.get("NumberHouse", ""))
    house_name = decode_unicode(raw.get("NameHouse", ""))
    floor_text = decode_unicode(raw.get("Floor", ""))
    floor_total_text = decode_unicode(raw.get("FloorTotal", ""))
    area_text = decode_unicode(raw.get("Square", ""))

    import re
    def extract_int(text: str) -> int:
        m = re.search(r"(\d+)", text or "")
        return int(m.group(1)) if m else 0

    def extract_float(text: str) -> float:
        m = re.search(r"(\d+(?:[\.,]\d+)?)", text or "")
        if m:
            return float(m.group(1).replace(",", "."))
        return 0.0

    floor = extract_int(floor_text)
    floor_total = extract_int(floor_total_text)
    area_m2 = extract_float(area_text)

    price_per_m2_eur = safe_float(raw.get("Price_metr"))
    price_total_eur = safe_float(raw.get("Price_full"))

    normalized: Dict[str, Any] = {
        "id": str(item_id),
        "complex": "Минск-Мир",
        "house_number": house_number or None,
        "unit_type": unit_type_norm,
        "unit_number": unit_number,
        "entrance": None,
        "floor": floor if floor else None,
        "rooms_possible": None,
        "area_m2": round(area_m2, 2) if area_m2 else None,
        "status": status or None,
        "quarter": quarter or None,
        "house_name": house_name or None,
        "address": address or None,
        "location": location or None,
        "price": {
            "per_m2": {"byn": None, "eur": int(price_per_m2_eur) if price_per_m2_eur else None},
            "total": {"byn": None, "eur": int(price_total_eur) if price_total_eur else None},
        },
        "contract": {"number": None, "date": None},
        "url": None,
        "meta": {
            "floor_total": floor_total if floor_total else None,
            "raw_type": raw_type or None,
        },
    }

    return normalized


def in_range(price_eur: Optional[float], pr: PriceRange) -> bool:
    if price_eur is None:
        return False
    lo, hi, _ = pr
    return lo <= price_eur < hi


def build_ranges(apartments: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Prepare buckets
    result = {
        "source": API_URL,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "price_ranges": []  # list of dicts
    }

    # helpers
    def total_price_eur(apt: Dict[str, Any]) -> float:
        total = apt.get("price", {}).get("total", {}).get("eur")
        return float(total) if total is not None else float("inf")

    TARGET_FLATS = 3
    TARGET_APARTS = 1

    for lo, hi, label in PRICE_RANGES:
        band_all: List[Dict[str, Any]] = [
            a for a in apartments
            if in_range(a.get("price", {}).get("total", {}).get("eur"), (lo, hi, label))
        ]
        # split by type
        band_flats = [a for a in band_all if (a.get("unit_type") == "Квартира")]
        band_aparts = [a for a in band_all if (a.get("unit_type") == "Апартаменты")]
        # take cheapest per group
        band_flats_sorted = sorted(band_flats, key=total_price_eur)[:TARGET_FLATS]
        band_aparts_sorted = sorted(band_aparts, key=total_price_eur)[:TARGET_APARTS]
        band_apts = band_flats_sorted + band_aparts_sorted

        result["price_ranges"].append({
            "label": label,
            "min_eur": lo,
            "max_eur": hi,
            "apartments": band_apts,
        })

    return result


def fetch_api() -> Dict[str, Any]:
    resp = requests.get(API_URL, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main() -> int:
    try:
        raw_data = fetch_api()
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return 1

    apartments: List[Dict[str, Any]] = []
    for item_id, raw in raw_data.items():
        normalized = normalize_apartment(str(item_id), raw)
        if not normalized:
            continue
        # keep only with known total price
        total_eur = normalized.get("price", {}).get("total", {}).get("eur")
        if total_eur is None or total_eur <= 0:
            continue
        apartments.append(normalized)

    result = build_ranges(apartments)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Готово: записано {len(apartments)} квартир в '{OUTPUT_PATH}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())


