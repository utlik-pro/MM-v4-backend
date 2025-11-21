#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание файла с объектами без указания квартала (Диадема и другие)
"""

import json
import requests
import re
from collections import defaultdict

def decode_unicode(text):
    """Декодирует Unicode последовательности"""
    if not text:
        return ""
    if not isinstance(text, str):
        return str(text)
    try:
        if text.startswith('\\u'):
            return text.encode('utf-8').decode('unicode_escape')
        return text
    except:
        return text

def extract_square(square_text):
    """Извлекает площадь из текста"""
    if not square_text:
        return 0.0
    decoded = decode_unicode(str(square_text))
    match = re.search(r'(\d+(?:\.\d+)?)', decoded)
    if match:
        return float(match.group(1))
    return 0.0

def main():
    print("📥 Загрузка данных для поиска пропущенных объектов...")
    
    # Загружаем данные
    url = "https://bir.by/ai/json_ai.php"
    response = requests.get(url, timeout=30)
    data = response.json()
    
    # Ищем объекты без квартала
    missing_objects = []
    diadema_objects = []
    
    for item_id, item in data.items():
        # Декодируем поля
        apartment = decode_unicode(item.get('Apartment', '')).strip()
        obj_type = decode_unicode(item.get('type', '')).strip()
        quarter = decode_unicode(item.get('Quarter', '')).strip()
        house_name = decode_unicode(item.get('NameHouse', '')).strip()
        house_number = decode_unicode(item.get('NumberHouse', '')).strip()
        address = decode_unicode(item.get('Address', '')).strip()
        status = decode_unicode(item.get('Status', '')).strip()
        location = decode_unicode(item.get('Location', '')).strip()
        floor = decode_unicode(item.get('Floor', '')).strip()
        floor_total = decode_unicode(item.get('FloorTotal', '')).strip()
        
        # Извлекаем числовые значения
        square = extract_square(item.get('Square', ''))
        price_metr = item.get('Price_metr', 0)
        price_full = item.get('Price_full', 0)
        
        # Пропускаем машиноместа
        if 'машиноместо' in obj_type.lower() or 'машиноместо' in apartment.lower():
            continue
        if 'паркинг' in house_name.lower():
            continue
            
        # Проверяем объекты без квартала или с проблемным кварталом
        if not quarter or quarter == '' or len(quarter) < 3:
            obj_data = {
                'id': item_id,
                'apartment': apartment,
                'type': obj_type,
                'house_name': house_name,
                'house_number': house_number,
                'address': address,
                'floor': floor,
                'floor_total': floor_total,
                'square': square,
                'price_metr': price_metr,
                'price_full': price_full,
                'status': status,
                'location': location
            }
            
            missing_objects.append(obj_data)
            
            # Особо выделяем Диадему
            if 'диадема' in house_name.lower() or 'diadema' in house_name.lower():
                diadema_objects.append(obj_data)
    
    print(f"✅ Найдено объектов без квартала: {len(missing_objects)}")
    print(f"   Из них в комплексе Диадема: {len(diadema_objects)}")
    
    # Создаем Markdown файл для Диадемы
    if diadema_objects:
        markdown = "# 🏢 Комплекс Диадема (Эмиратс)\n\n"
        markdown += "## 📍 Общая информация\n"
        markdown += "**Комплекс:** Диадема (Emirates)\n"
        markdown += "**Адрес:** проспект Мира, дом 1\n"
        markdown += "**Район:** Минск Мир\n"
        markdown += f"**Количество объектов:** {len(diadema_objects)}\n\n"
        markdown += "---\n\n"
        
        # Группируем по этажам
        by_floor = defaultdict(list)
        for obj in diadema_objects:
            floor_num = re.search(r'(\d+)', obj['floor'])
            floor_key = int(floor_num.group(1)) if floor_num else 0
            by_floor[floor_key].append(obj)
        
        # Статистика
        prices = [obj['price_metr'] for obj in diadema_objects if obj['price_metr'] > 0]
        squares = [obj['square'] for obj in diadema_objects if obj['square'] > 0]
        costs = [obj['price_full'] for obj in diadema_objects if obj['price_full'] > 0]
        
        if prices or squares or costs:
            markdown += "## 📊 Статистика комплекса\n"
            if squares:
                markdown += f"**Диапазон площадей:** {min(squares):.1f} - {max(squares):.1f} м²\n"
            if prices:
                markdown += f"**Средняя цена за м²:** {sum(prices)/len(prices):.0f} евро\n"
            if costs:
                markdown += f"**Средняя стоимость:** {sum(costs)/len(costs):.0f} евро\n"
            markdown += "\n---\n\n"
        
        # Выводим по этажам
        for floor_num in sorted(by_floor.keys()):
            if floor_num > 0:
                markdown += f"## 🏢 Этаж {floor_num}\n\n"
                
                for obj in by_floor[floor_num]:
                    markdown += f"### 🏠 {obj['apartment']}\n"
                    if obj['type']:
                        markdown += f"**Тип:** {obj['type']}\n"
                    if obj['address']:
                        markdown += f"**Адрес:** {obj['address']}\n"
                    markdown += f"**Этаж:** {obj['floor']}\n"
                    if obj['floor_total']:
                        markdown += f"**Всего этажей:** {obj['floor_total']}\n"
                    if obj['square'] > 0:
                        markdown += f"**Площадь:** {obj['square']:.1f} м²\n"
                    if obj['price_metr'] > 0:
                        markdown += f"**Цена за м²:** {obj['price_metr']:.0f} евро\n"
                    if obj['price_full'] > 0:
                        markdown += f"**Общая стоимость:** {obj['price_full']:,.0f} евро\n"
                    if obj['status']:
                        markdown += f"**Статус:** {obj['status']}\n"
                    if obj['location']:
                        markdown += f"**Местоположение:** {obj['location']}\n"
                    markdown += "\n---\n\n"
        
        # Сохраняем файл
        with open('quarters/02-emirats-diadema.md', 'w', encoding='utf-8') as f:
            f.write(markdown)
        print("📄 Создан файл: quarters/02-emirats-diadema.md")
    
    # Проверяем другие пропущенные объекты
    other_missing = [obj for obj in missing_objects if obj not in diadema_objects]
    if other_missing:
        print(f"\n⚠️ Другие объекты без квартала: {len(other_missing)}")
        
        # Группируем по адресам
        by_address = defaultdict(list)
        for obj in other_missing:
            by_address[obj['address']].append(obj)
        
        for address, objects in list(by_address.items())[:5]:
            print(f"  • {address}: {len(objects)} объектов")
            for obj in objects[:2]:
                print(f"    - {obj['apartment']} ({obj['type']})")
    
    # Сохраняем полный список
    with open('missing_objects_full_list.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_missing': len(missing_objects),
            'diadema': diadema_objects,
            'other': other_missing
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Полный список сохранен: missing_objects_full_list.json")

if __name__ == "__main__":
    main()