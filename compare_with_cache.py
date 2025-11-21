#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сравнение текущих данных с кэшированными данными
"""

import json
import os
from datetime import datetime

def load_json(filepath):
    """Загружает JSON файл"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки {filepath}: {e}")
        return None

def main():
    print("🔍 Сравнение данных недвижимости")
    print("="*60)
    
    # Загружаем текущий снимок
    current_data = load_json('data_snapshots/snapshot_20250922_092706.json')
    if not current_data:
        print("Не удалось загрузить текущие данные")
        return
    
    # Загружаем предыдущие данные из кэша
    previous_data = load_json('cache/previous_data.json')
    if not previous_data:
        print("Не удалось загрузить предыдущие данные")
        return
    
    print(f"📊 Текущие данные: {len(current_data)} объектов")
    print(f"📂 Предыдущие данные (из кэша): {len(previous_data)} объектов")
    print(f"🔄 Разница: {len(current_data) - len(previous_data):+d} объектов\n")
    
    # Сравниваем ID
    current_ids = set(current_data.keys())
    previous_ids = set(previous_data.keys())
    
    added = current_ids - previous_ids
    removed = previous_ids - current_ids
    common = current_ids & previous_ids
    
    print("📈 ИЗМЕНЕНИЯ:")
    print(f"  ✅ Добавлено новых: {len(added)}")
    print(f"  ❌ Удалено (продано?): {len(removed)}")
    print(f"  🔄 Общих объектов: {len(common)}")
    print()
    
    # Проверяем изменения цен
    price_changes = []
    status_changes = []
    
    for item_id in common:
        curr = current_data[item_id]
        prev = previous_data[item_id]
        
        # Проверяем изменение цены
        curr_price = curr.get('Price_full', 0)
        prev_price = prev.get('Price_full', 0)
        
        if curr_price != prev_price:
            price_changes.append({
                'id': item_id,
                'apartment': curr.get('Apartment', 'N/A'),
                'quarter': curr.get('Quarter', 'N/A'),
                'old_price': prev_price,
                'new_price': curr_price,
                'change': curr_price - prev_price
            })
        
        # Проверяем изменение статуса
        if curr.get('Status') != prev.get('Status'):
            status_changes.append({
                'id': item_id,
                'apartment': curr.get('Apartment', 'N/A'),
                'old_status': prev.get('Status', 'N/A'),
                'new_status': curr.get('Status', 'N/A')
            })
    
    # Выводим изменения цен
    if price_changes:
        print("💰 ИЗМЕНЕНИЯ ЦЕН:")
        sorted_prices = sorted(price_changes, key=lambda x: abs(x['change']), reverse=True)
        for i, change in enumerate(sorted_prices[:10], 1):
            if change['old_price'] > 0:
                percent = (change['change'] / change['old_price']) * 100
                emoji = "📈" if change['change'] > 0 else "📉"
                print(f"  {i}. {emoji} {change['apartment']}")
                print(f"     Квартал: {change['quarter']}")
                print(f"     Было: {change['old_price']:.0f} EUR → Стало: {change['new_price']:.0f} EUR")
                print(f"     Изменение: {change['change']:+.0f} EUR ({percent:+.1f}%)")
        if len(price_changes) > 10:
            print(f"  ... и еще {len(price_changes) - 10} изменений цен")
        print()
    
    # Выводим новые объекты
    if added:
        print("✅ ПРИМЕРЫ НОВЫХ ОБЪЕКТОВ:")
        for i, item_id in enumerate(list(added)[:10], 1):
            item = current_data[item_id]
            print(f"  {i}. {item.get('Apartment', 'N/A')}")
            print(f"     Квартал: {item.get('Quarter', 'N/A')}")
            print(f"     Площадь: {item.get('Square', 'N/A')} м²")
            print(f"     Цена: {item.get('Price_full', 'N/A')} EUR")
        if len(added) > 10:
            print(f"  ... и еще {len(added) - 10} новых объектов")
        print()
    
    # Выводим удаленные объекты
    if removed:
        print("❌ ПРИМЕРЫ УДАЛЕННЫХ ОБЪЕКТОВ (возможно проданы):")
        for i, item_id in enumerate(list(removed)[:10], 1):
            item = previous_data[item_id]
            print(f"  {i}. {item.get('Apartment', 'N/A')}")
            print(f"     Квартал: {item.get('Quarter', 'N/A')}")
            print(f"     Площадь: {item.get('Square', 'N/A')} м²")
            print(f"     Была цена: {item.get('Price_full', 'N/A')} EUR")
        if len(removed) > 10:
            print(f"  ... и еще {len(removed) - 10} удаленных объектов")
        print()
    
    # Сохраняем детальный отчет
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'current_total': len(current_data),
            'previous_total': len(previous_data),
            'added': len(added),
            'removed': len(removed),
            'price_changes': len(price_changes),
            'status_changes': len(status_changes)
        },
        'added_ids': list(added),
        'removed_ids': list(removed),
        'price_changes': price_changes,
        'status_changes': status_changes
    }
    
    report_file = f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Детальный отчет сохранен: {report_file}")
    print("✅ Проверка завершена!")

if __name__ == "__main__":
    main()