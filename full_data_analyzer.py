#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полный анализ ВСЕХ объектов с bir.by включая специальные случаи
"""

import json
import requests
from collections import defaultdict
import re

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

def main():
    print("🔍 Полный анализ данных недвижимости BIR.BY")
    print("=" * 60)
    
    # Загружаем данные
    url = "https://bir.by/ai/json_ai.php"
    print(f"📥 Загрузка данных с {url}...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return
    
    print(f"✅ Загружено объектов: {len(data)}")
    
    # Анализируем типы объектов
    types_count = defaultdict(int)
    quarters_count = defaultdict(int)
    special_objects = []
    parking_objects = []
    residential_objects = []
    unknown_quarter_objects = []
    emirates_objects = []
    
    for item_id, item in data.items():
        # Декодируем поля
        obj_type = decode_unicode(item.get('type', '')).strip()
        apartment = decode_unicode(item.get('Apartment', '')).strip()
        quarter = decode_unicode(item.get('Quarter', '')).strip()
        house_name = decode_unicode(item.get('NameHouse', '')).strip()
        address = decode_unicode(item.get('Address', '')).strip()
        square = item.get('Square', '')
        price = item.get('Price_full', 0)
        
        # Извлекаем площадь
        if square:
            square_match = re.search(r'(\d+(?:\.\d+)?)', str(square))
            square_val = float(square_match.group(1)) if square_match else 0
        else:
            square_val = 0
        
        # Классифицируем объект
        obj_lower = obj_type.lower()
        apt_lower = apartment.lower()
        house_lower = house_name.lower()
        
        # Проверяем на машиноместо
        is_parking = False
        if 'машиноместо' in obj_lower or 'машиноместо' in apt_lower:
            is_parking = True
        elif 'паркинг' in house_lower or 'parking' in house_lower:
            is_parking = True
        elif square_val > 0 and square_val < 20 and price < 25000:
            # Маленькая площадь и низкая цена - вероятно паркинг
            if 'квартира' not in apt_lower and 'апартамент' not in apt_lower:
                is_parking = True
        
        if is_parking:
            parking_objects.append({
                'id': item_id,
                'type': obj_type,
                'apartment': apartment,
                'quarter': quarter,
                'house': house_name,
                'square': square_val,
                'price': price
            })
        else:
            residential_objects.append({
                'id': item_id,
                'type': obj_type,
                'apartment': apartment,
                'quarter': quarter,
                'house': house_name,
                'address': address,
                'square': square_val,
                'price': price
            })
            
            # Проверяем на Эмиратс
            if 'эмиратс' in house_lower or 'emirats' in house_lower or 'emirates' in house_lower:
                emirates_objects.append({
                    'id': item_id,
                    'apartment': apartment,
                    'house': house_name,
                    'address': address,
                    'quarter': quarter
                })
            
            # Проверяем на пустой квартал
            if not quarter or quarter == '' or 'неизвестн' in quarter.lower():
                unknown_quarter_objects.append({
                    'id': item_id,
                    'apartment': apartment,
                    'house': house_name,
                    'address': address
                })
        
        # Подсчитываем типы
        if obj_type:
            types_count[obj_type] += 1
        else:
            types_count['Без типа'] += 1
        
        # Подсчитываем кварталы
        if quarter:
            # Извлекаем название квартала
            match = re.search(r'Квартал\s*[—\-]\s*(.+)', quarter)
            if match:
                quarter_name = match.group(1).strip()
                quarters_count[quarter_name] += 1
            else:
                quarters_count[quarter] += 1
        else:
            quarters_count['Без квартала'] += 1
    
    # Выводим статистику
    print("\n📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"  • Всего объектов: {len(data)}")
    print(f"  • Машиномест: {len(parking_objects)}")
    print(f"  • Жилых объектов: {len(residential_objects)}")
    print(f"  • Объектов без квартала: {len(unknown_quarter_objects)}")
    print(f"  • Объектов Эмиратс: {len(emirates_objects)}")
    
    print("\n📈 ТИПЫ ОБЪЕКТОВ:")
    for obj_type, count in sorted(types_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  • {obj_type}: {count}")
    
    print("\n🏘️ КВАРТАЛЫ (топ-15):")
    for quarter, count in sorted(quarters_count.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  • {quarter}: {count} объектов")
    
    # Анализ объектов без квартала
    if unknown_quarter_objects:
        print(f"\n⚠️ ОБЪЕКТЫ БЕЗ КВАРТАЛА ({len(unknown_quarter_objects)} шт):")
        
        # Группируем по домам
        by_house = defaultdict(list)
        for obj in unknown_quarter_objects[:50]:  # Первые 50
            house = obj['house'] if obj['house'] else 'Без названия'
            by_house[house].append(obj)
        
        for house, objects in sorted(by_house.items())[:10]:
            print(f"\n  🏠 {house} ({len(objects)} объектов):")
            for obj in objects[:3]:
                print(f"    - {obj['apartment']}")
                print(f"      Адрес: {obj['address']}")
    
    # Анализ Эмиратс
    if emirates_objects:
        print(f"\n🏢 ОБЪЕКТЫ ЭМИРАТС ({len(emirates_objects)} шт):")
        emirates_by_house = defaultdict(list)
        for obj in emirates_objects:
            emirates_by_house[obj['house']].append(obj)
        
        for house, objects in sorted(emirates_by_house.items()):
            print(f"  • {house}: {len(objects)} объектов")
            if objects[0]['quarter']:
                print(f"    Квартал: {objects[0]['quarter']}")
    
    # Сохраняем полные данные для анализа
    with open('full_analysis_report.json', 'w', encoding='utf-8') as f:
        report = {
            'total_objects': len(data),
            'parking_count': len(parking_objects),
            'residential_count': len(residential_objects),
            'unknown_quarter_count': len(unknown_quarter_objects),
            'emirates_count': len(emirates_objects),
            'types': dict(types_count),
            'quarters': dict(quarters_count),
            'unknown_quarter_objects': unknown_quarter_objects[:100],  # Первые 100
            'emirates_objects': emirates_objects
        }
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Детальный отчет сохранен: full_analysis_report.json")
    
    # Проверяем, есть ли объекты, которые могли быть упущены
    print("\n🔍 ПРОВЕРКА НА УПУЩЕННЫЕ ОБЪЕКТЫ:")
    
    # Проверяем объекты с необычными полями
    unusual_objects = []
    for item_id, item in data.items():
        apartment = decode_unicode(item.get('Apartment', '')).strip()
        
        # Проверяем специальные типы
        if any(keyword in apartment.lower() for keyword in ['пентхаус', 'penthouse', 'бизнес', 'business', 'студия', 'studio']):
            obj_type = decode_unicode(item.get('type', ''))
            if 'машиноместо' not in obj_type.lower():
                unusual_objects.append({
                    'id': item_id,
                    'apartment': apartment,
                    'type': obj_type,
                    'quarter': decode_unicode(item.get('Quarter', '')),
                    'price': item.get('Price_full', 0)
                })
    
    if unusual_objects:
        print(f"  Найдено специальных объектов: {len(unusual_objects)}")
        for obj in unusual_objects[:5]:
            print(f"    • {obj['apartment']} - {obj['type']}")

if __name__ == "__main__":
    main()