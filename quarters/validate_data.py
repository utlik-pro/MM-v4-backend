#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система валидации и проверки данных квартир
"""

import json
import re
import os
from collections import defaultdict, Counter
import urllib.request
from datetime import datetime

def fetch_api_data():
    """Загрузка данных из API"""
    api_url = 'https://bir.by/ai/json_ai.php'
    try:
        with urllib.request.urlopen(api_url, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Ошибка при загрузке API: {e}")
        return None

def validate_apartments():
    """Полная валидация данных"""
    print("\n" + "="*70)
    print("🔍 СИСТЕМА ВАЛИДАЦИИ ДАННЫХ КВАРТИР")
    print("="*70)
    
    # Загрузка данных
    api_data = fetch_api_data()
    if not api_data:
        return
    
    print(f"\n📊 Загружено объектов: {len(api_data)}")
    
    # Проблемы для отчета
    issues = {
        'missing_quarter': [],
        'duplicate_apartments': [],
        'invalid_status': [],
        'missing_fields': defaultdict(list),
        'invalid_prices': [],
        'house_name_mismatch': defaultdict(list),
        'floor_issues': []
    }
    
    # Счетчики
    quarters_count = Counter()
    statuses_count = Counter()
    apartments_by_quarter_house = defaultdict(lambda: defaultdict(list))
    
    # Валидные статусы
    valid_statuses = [
        'Статус: Сдано',
        'Статус: Строится', 
        'Статус: Строящаяся квартира',
        'Статус: Строящиеся Бизнес-апартаменты'
    ]
    
    print("\n🔍 Анализ данных...\n")
    
    for key, apt in api_data.items():
        apt_name = apt.get('Apartment', f'Unknown_{key}')
        
        # 1. Проверка квартала
        quarter = apt.get('Quarter', '')
        if not quarter or 'Квартал — ' not in quarter:
            issues['missing_quarter'].append({
                'apartment': apt_name,
                'house': apt.get('NameHouse', ''),
                'address': apt.get('Address', '')
            })
        else:
            quarter_clean = quarter.replace('Квартал — ', '').strip()
            quarters_count[quarter_clean] += 1
            
            # Группировка по кварталу и дому
            house = apt.get('NumberHouse', '')
            apartments_by_quarter_house[quarter_clean][house].append(apt_name)
        
        # 2. Проверка статуса
        status = apt.get('Status', '')
        statuses_count[status] += 1
        if status and not any(vs in status for vs in valid_statuses):
            if 'Продано' not in status and 'Забронировано' not in status:
                issues['invalid_status'].append({
                    'apartment': apt_name,
                    'status': status
                })
        
        # 3. Проверка обязательных полей
        required_fields = ['NumberHouse', 'NameHouse', 'Floor', 'Square', 'UsrNumberRooms']
        for field in required_fields:
            if not apt.get(field) or apt.get(field) == 'Н/Д':
                issues['missing_fields'][field].append(apt_name)
        
        # 4. Проверка цен
        price_m = apt.get('Price_metr')
        price_f = apt.get('Price_full')
        if price_m and price_m != '—':
            try:
                if isinstance(price_m, (int, float)):
                    if price_m < 500 or price_m > 10000:
                        issues['invalid_prices'].append({
                            'apartment': apt_name,
                            'price_metr': price_m
                        })
            except:
                pass
        
        # 5. Проверка этажа
        floor = apt.get('Floor', '')
        if floor:
            floor_match = re.search(r'Этаж: (\d+)', floor)
            if floor_match:
                floor_num = int(floor_match.group(1))
                if floor_num > 30 or floor_num < 1:
                    issues['floor_issues'].append({
                        'apartment': apt_name,
                        'floor': floor_num
                    })
    
    # Поиск дубликатов
    for quarter, houses in apartments_by_quarter_house.items():
        for house, apts in houses.items():
            apt_counter = Counter(apts)
            for apt, count in apt_counter.items():
                if count > 1:
                    issues['duplicate_apartments'].append({
                        'apartment': apt,
                        'quarter': quarter,
                        'house': house,
                        'count': count
                    })
    
    # ОТЧЕТ О ПРОБЛЕМАХ
    print("\n" + "="*70)
    print("📋 ОТЧЕТ О НАЙДЕННЫХ ПРОБЛЕМАХ")
    print("="*70)
    
    # 1. Квартиры без квартала
    if issues['missing_quarter']:
        print(f"\n❌ Квартиры без указания квартала: {len(issues['missing_quarter'])}")
        for item in issues['missing_quarter'][:5]:  # Показываем первые 5
            print(f"   - {item['apartment']} (Дом: {item['house']}, Адрес: {item['address']})")
        if len(issues['missing_quarter']) > 5:
            print(f"   ... и еще {len(issues['missing_quarter'])-5} квартир")
    
    # 2. Дубликаты
    if issues['duplicate_apartments']:
        print(f"\n❌ Найдены дубликаты квартир: {len(issues['duplicate_apartments'])}")
        for dup in issues['duplicate_apartments'][:3]:
            print(f"   - {dup['apartment']} в квартале {dup['quarter']}, дом {dup['house']} (повторяется {dup['count']} раз)")
    
    # 3. Некорректные статусы
    if issues['invalid_status']:
        print(f"\n⚠️ Квартиры с неизвестными статусами: {len(issues['invalid_status'])}")
        unique_statuses = set(item['status'] for item in issues['invalid_status'])
        for status in list(unique_statuses)[:5]:
            print(f"   - Статус: '{status}'")
    
    # 4. Отсутствующие поля
    if issues['missing_fields']:
        print("\n⚠️ Отсутствующие данные:")
        for field, apartments in issues['missing_fields'].items():
            if apartments:
                print(f"   - Поле '{field}': {len(apartments)} квартир")
    
    # 5. Проблемы с ценами
    if issues['invalid_prices']:
        print(f"\n⚠️ Подозрительные цены: {len(issues['invalid_prices'])} квартир")
        for item in issues['invalid_prices'][:3]:
            print(f"   - {item['apartment']}: {item['price_metr']} евро/м²")
    
    # 6. Проблемы с этажами
    if issues['floor_issues']:
        print(f"\n⚠️ Некорректные этажи: {len(issues['floor_issues'])} квартир")
        for item in issues['floor_issues'][:3]:
            print(f"   - {item['apartment']}: этаж {item['floor']}")
    
    # СТАТИСТИКА ПО КВАРТАЛАМ
    print("\n" + "="*70)
    print("📊 СТАТИСТИКА ПО КВАРТАЛАМ")
    print("="*70)
    
    for quarter, count in sorted(quarters_count.items()):
        print(f"  {quarter}: {count} квартир")
    
    # СТАТИСТИКА ПО СТАТУСАМ
    print("\n📊 СТАТИСТИКА ПО СТАТУСАМ:")
    for status, count in sorted(statuses_count.items()):
        if count > 0:
            print(f"  {status}: {count}")
    
    # РЕКОМЕНДАЦИИ
    print("\n" + "="*70)
    print("💡 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ")
    print("="*70)
    
    if issues['missing_quarter']:
        print("\n1. Для квартир без квартала:")
        print("   - Проверить адреса и названия домов")
        print("   - Добавить маппинг по адресам в скрипт")
    
    if issues['duplicate_apartments']:
        print("\n2. Для дубликатов:")
        print("   - Проверить уникальность ID в API")
        print("   - Добавить фильтрацию дубликатов")
    
    if issues['invalid_status']:
        print("\n3. Для неизвестных статусов:")
        print("   - Обновить список валидных статусов")
        print("   - Связаться с API провайдером")
    
    # Сохранение отчета
    report_path = '/Users/admin/MM-RAG/quarters/validation_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_objects': len(api_data),
            'issues': {
                'missing_quarter': len(issues['missing_quarter']),
                'duplicate_apartments': len(issues['duplicate_apartments']),
                'invalid_status': len(issues['invalid_status']),
                'missing_fields': {k: len(v) for k, v in issues['missing_fields'].items()},
                'invalid_prices': len(issues['invalid_prices']),
                'floor_issues': len(issues['floor_issues'])
            },
            'details': issues
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 Подробный отчет сохранен в: {report_path}")
    
    # Проверка конкретных проблемных кварталов
    print("\n" + "="*70)
    print("🔍 ПРОВЕРКА КРИТИЧЕСКИХ КВАРТАЛОВ")
    print("="*70)
    
    # Проверка Хельсинки
    helsinki_apts = []
    for key, apt in api_data.items():
        if 'Хельсинки' in apt.get('NameHouse', '') or 'Хе́льсинки' in apt.get('NameHouse', ''):
            helsinki_apts.append(apt)
    
    print(f"\n🏠 Дом Хельсинки: {len(helsinki_apts)} квартир")
    for apt in helsinki_apts:
        print(f"   - {apt.get('Apartment')} | Квартал: {apt.get('Quarter', 'НЕ УКАЗАН')} | Статус: {apt.get('Status')}")
    
    return issues

if __name__ == "__main__":
    issues = validate_apartments()
    
    # Возвращаем код ошибки если есть критические проблемы
    if issues and (issues['missing_quarter'] or issues['duplicate_apartments']):
        exit(1)
    else:
        exit(0)