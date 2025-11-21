#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный скрипт обновления с исправлением ошибок
"""

import json
import re
import os
import sys
import logging
from datetime import datetime
from collections import defaultdict, Counter
import urllib.request

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Маппинг кварталов к файлам
QUARTER_MAPPINGS = {
    '7 Средиземноморский': '7-Sredizemnomorskiy.md',
    '9 Южная Америка': '9-Yuzhnaya-Amerika.md',
    '10 Тропические острова': '10-Tropicheskie-ostrova.md',
    '11 Австралия и Океания': '11-Avstraliya-i-Okeaniya.md',
    '12 Западная Европа': '12-Zapadnaya-Evropa.md',
    '16 Родная страна': '16-Rodnaya-strana.md',
    '18 Чемпионов': '18-Chempionov.md',
    '19 Южная Европа': '19-Yuzhnaya-Evropa.md',
    '20 Мировых танцев': '20-Mirovyh-tantsev.md',
    '21 Западный': '21-Zapadnyy.md',
    '22 Центральная Европа': '22-Tsentralnaya-Evropa.md',
    '23 Евразия': '23-Evraziya.md',
    '25 Азия': '25-Aziya.md',
    '26 Африка': '26-Afrika.md',
    '27 Happy Planet': '27-Happy-Planet.md',
    '28 Happy Planet': '28-Happy-Planet.md',
    '29 Северная Европа': '29-Severnaya-Evropa.md',
    '30 Северная Америка': '30-Severnaya-Amerika.md',
    '02 Эмиратс': '02-emirats.md',
    '2 Эмиратс': '02-emirats.md'  # Дополнительный вариант
}

# Маппинг по домам для неизвестных кварталов
HOUSE_TO_QUARTER = {
    'Диадема': '02 Эмиратс',  # Диадема относится к Эмиратс
    'Эмиратс': '02 Эмиратс',
    'Emirates': '02 Эмиратс'
}

# Маппинг по адресам
ADDRESS_TO_QUARTER = {
    'проспект Мира, дом 1': '02 Эмиратс'
}

# Валидные статусы
VALID_STATUSES = [
    'Статус: Сдано',
    'Статус: Строится',
    'Статус: Строящаяся квартира',
    'Статус: Строящиеся Бизнес-апартаменты'
]

def fetch_api_data():
    """Загрузка данных из API"""
    api_url = 'https://bir.by/ai/json_ai.php'
    try:
        with urllib.request.urlopen(api_url, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            logger.info(f"Загружено {len(data)} объектов из API")
            return data
    except Exception as e:
        logger.error(f"Ошибка при загрузке API: {e}")
        return None

def determine_quarter(apartment):
    """Определение квартала для квартиры"""
    # 1. Проверяем явно указанный квартал
    quarter_field = apartment.get('Quarter', '')
    if 'Квартал — ' in quarter_field:
        return quarter_field.replace('Квартал — ', '').strip()
    
    # 2. Проверяем по названию дома
    house_name = apartment.get('NameHouse', '')
    for house_key, quarter in HOUSE_TO_QUARTER.items():
        if house_key in house_name:
            logger.debug(f"Квартира {apartment.get('Apartment')} определена в {quarter} по дому {house_name}")
            return quarter
    
    # 3. Проверяем по номеру дома
    house_number = apartment.get('NumberHouse', '')
    for house_key, quarter in HOUSE_TO_QUARTER.items():
        if house_key in house_number:
            logger.debug(f"Квартира {apartment.get('Apartment')} определена в {quarter} по номеру дома {house_number}")
            return quarter
    
    # 4. Проверяем по адресу
    address = apartment.get('Address', '')
    for addr_key, quarter in ADDRESS_TO_QUARTER.items():
        if addr_key in address:
            logger.debug(f"Квартира {apartment.get('Apartment')} определена в {quarter} по адресу {address}")
            return quarter
    
    return None

def validate_apartment_data(apartment):
    """Валидация данных квартиры"""
    warnings = []
    
    # Проверка обязательных полей
    required_fields = ['Apartment', 'NumberHouse', 'Floor']
    for field in required_fields:
        if not apartment.get(field):
            warnings.append(f"Отсутствует поле {field}")
    
    # Проверка этажа
    floor_str = apartment.get('Floor', '')
    if floor_str and 'Этаж: ' in floor_str:
        try:
            floor_num = int(floor_str.replace('Этаж: ', ''))
            if floor_num < 1 or floor_num > 30:
                warnings.append(f"Подозрительный этаж: {floor_num}")
        except:
            warnings.append(f"Некорректный формат этажа: {floor_str}")
    
    # Проверка цен
    price_m = apartment.get('Price_metr')
    if price_m and price_m != '—' and isinstance(price_m, (int, float)):
        if price_m < 500 or price_m > 10000:
            warnings.append(f"Подозрительная цена за м²: {price_m}")
    
    return warnings

def generate_apartment_section(apartment):
    """Генерация секции для квартиры"""
    quarter_field = apartment.get('Quarter', '')
    if 'Квартал — ' in quarter_field:
        quarter_name = quarter_field.replace('Квартал — ', '').strip()
    else:
        # Пытаемся определить квартал
        quarter_name = determine_quarter(apartment) or ''
    
    apt_name = apartment.get('Apartment', 'Квартира')
    
    section = f"### 🏠 {apt_name}\n"
    section += f"**Квартал:** {quarter_name}\n"
    section += f"**Дом:** {apartment.get('NumberHouse', 'Н/Д')}\n"
    section += f"**Название дома:** {apartment.get('NameHouse', 'Н/Д')}\n"
    section += f"**{apartment.get('Floor', 'Этаж: Н/Д')}**\n"
    section += f"**{apartment.get('FloorTotal', 'Этажность дома: Н/Д')}**\n"
    section += f"**Количество комнат:** {apartment.get('UsrNumberRooms', 'Н/Д')}\n"
    section += f"**{apartment.get('Square', 'Площадь: Н/Д')}**\n"
    
    price_metr = apartment.get('Price_metr')
    if price_metr and price_metr != '—':
        section += f"**Цена за м²:** {price_metr:,} евро\n" if isinstance(price_metr, (int, float)) else f"**Цена за м²:** {price_metr} евро\n"
    
    price_full = apartment.get('Price_full')
    if price_full and price_full != '—':
        section += f"**Общая стоимость:** {price_full:,} евро\n" if isinstance(price_full, (int, float)) else f"**Общая стоимость:** {price_full} евро\n"
    
    section += f"**{apartment.get('Status', 'Статус: Н/Д')}**\n"
    section += f"**Адрес:** {apartment.get('Address', 'Н/Д')}\n"
    section += f"**{apartment.get('Location', 'Местоположение: Н/Д')}**\n"
    
    return section

def update_quarter_file(file_path, quarter_name, apartments_data):
    """Обновление файла квартала"""
    houses = defaultdict(lambda: defaultdict(list))
    
    # Проверка и группировка квартир
    apartments_seen = set()  # Для отслеживания дубликатов
    
    for apt in apartments_data:
        # Создаем уникальный ключ
        apt_key = f"{apt.get('Apartment')}_{apt.get('NumberHouse')}_{apt.get('Floor')}"
        
        # Пропускаем дубликаты
        if apt_key in apartments_seen:
            logger.warning(f"Обнаружен дубликат: {apt.get('Apartment')} в квартале {quarter_name}")
            continue
        apartments_seen.add(apt_key)
        
        # Валидация
        warnings = validate_apartment_data(apt)
        if warnings:
            logger.debug(f"Предупреждения для {apt.get('Apartment')}: {', '.join(warnings)}")
        
        house = apt.get('NumberHouse', 'Unknown')
        floor = apt.get('Floor', 'Этаж: 0').replace('Этаж: ', '')
        try:
            floor_num = int(floor)
        except:
            floor_num = 0
        
        houses[house][floor_num].append(apt)
    
    # Генерация содержимого
    content = f"# 🏘️ Квартал — {quarter_name}\n\n"
    content += f"## 📍 Общая информация\n"
    content += f"**Квартал:** {quarter_name}\n"
    content += f"**Город:** Минск\n"
    content += f"**Район:** Мир\n"
    content += f"**Количество домов:** {len(houses)}\n"
    content += f"**Количество объектов:** {len(apartments_seen)}\n"
    
    types = set(apt.get('type', 'Квартира') for apt in apartments_data)
    content += f"**Типы недвижимости:** {', '.join(sorted(types))}\n"
    content += f"**Обновлено:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    content += "\n/n/n\n---\n\n"
    
    # Для каждого дома
    for house_num in sorted(houses.keys()):
        house_data = houses[house_num]
        house_apartments = [apt for floor_apts in house_data.values() for apt in floor_apts]
        
        if house_apartments:
            first_apt = house_apartments[0]
            house_name = first_apt.get('NameHouse', 'Н/Д')
            
            content += f"## 🏠 Дом {house_num}\n\n"
            content += f"**Название дома:** {house_name}\n\n"
            content += f"### 📊 Статистика дома\n"
            content += f"**Количество апартаментов:** {len(house_apartments)}\n"
            
            # Диапазон площадей
            areas = []
            for apt in house_apartments:
                area = apt.get('Square', '').replace('Площадь: ', '').replace(' м²', '')
                try:
                    areas.append(float(area))
                except:
                    pass
            
            if areas:
                content += f"**Диапазон площадей:** {min(areas):.1f} - {max(areas):.1f} м²\n"
            
            # Средние цены
            prices_metr = []
            prices_full = []
            for apt in house_apartments:
                price_m = apt.get('Price_metr')
                price_f = apt.get('Price_full')
                if price_m and price_m != '—' and isinstance(price_m, (int, float)):
                    prices_metr.append(price_m)
                if price_f and price_f != '—' and isinstance(price_f, (int, float)):
                    prices_full.append(price_f)
            
            if prices_metr:
                content += f"**Средняя цена за м²:** {int(sum(prices_metr) / len(prices_metr))} евро\n"
            if prices_full:
                content += f"**Средняя стоимость:** {int(sum(prices_full) / len(prices_full))} евро\n"
            
            content += "\n/n/n\n---\n\n"
            
            # Для каждого этажа
            for floor_num in sorted(house_data.keys()):
                if floor_num == 0:
                    continue
                
                content += f"## 🏢 Этаж {floor_num}\n\n"
                
                # Сортировка по количеству комнат
                floor_apartments = sorted(house_data[floor_num], 
                                         key=lambda x: (x.get('UsrNumberRooms', 0), 
                                                       x.get('Apartment', '')))
                
                for apt in floor_apartments:
                    content += generate_apartment_section(apt)
                    content += "\n/n/n\n---\n\n"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return len(apartments_seen)

def main():
    """Основная функция"""
    print("\n" + "="*70)
    print("🚀 ЗАПУСК УЛУЧШЕННОГО ОБНОВЛЕНИЯ С ПРОВЕРКОЙ ОШИБОК")
    print("="*70)
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Загрузка данных
    api_data = fetch_api_data()
    if not api_data:
        print("❌ Не удалось загрузить данные")
        return False
    
    print(f"📊 Загружено объектов: {len(api_data)}")
    
    # Группировка и фильтрация
    quarters_data = defaultdict(list)
    unknown_quarters = []
    filtered_count = 0
    duplicates = []
    
    # Счетчик для отслеживания дубликатов
    apartment_counter = Counter()
    
    for key, apartment in api_data.items():
        status = apartment.get('Status', '')
        
        # Проверяем статус
        if not any(valid_status in status for valid_status in VALID_STATUSES):
            filtered_count += 1
            continue
        
        # Определяем квартал
        quarter_name = determine_quarter(apartment)
        
        if quarter_name:
            quarters_data[quarter_name].append(apartment)
            
            # Проверка на дубликаты
            apt_id = f"{apartment.get('Apartment')}_{quarter_name}"
            apartment_counter[apt_id] += 1
            if apartment_counter[apt_id] > 1:
                duplicates.append(apt_id)
        else:
            unknown_quarters.append(apartment)
    
    print(f"📊 Отфильтровано (проданы/забронированы): {filtered_count}")
    
    if unknown_quarters:
        print(f"\n⚠️  Квартир без определенного квартала: {len(unknown_quarters)}")
        for apt in unknown_quarters[:5]:
            print(f"   - {apt.get('Apartment')} | Дом: {apt.get('NameHouse')} | Адрес: {apt.get('Address')}")
        if len(unknown_quarters) > 5:
            print(f"   ... и еще {len(unknown_quarters)-5} квартир")
    
    if duplicates:
        print(f"\n⚠️  Обнаружено дубликатов: {len(set(duplicates))}")
    
    # Распределение по кварталам
    print("\n📊 Распределение квартир по кварталам:")
    for quarter_name, apartments in sorted(quarters_data.items()):
        print(f"  {quarter_name}: {len(apartments)} квартир")
    
    # Обновление файлов
    quarters_dir = '/Users/admin/MM-RAG/quarters'
    total_updated = 0
    changes = {}
    
    print("\n📝 Обновление файлов...")
    for quarter_name, apartments in quarters_data.items():
        if quarter_name in QUARTER_MAPPINGS:
            file_name = QUARTER_MAPPINGS[quarter_name]
            file_path = os.path.join(quarters_dir, file_name)
            
            count = update_quarter_file(file_path, quarter_name, apartments)
            total_updated += count
            
            print(f"  ✅ {file_name}: {count} квартир")
    
    print("\n" + "="*70)
    print(f"✅ Обновление завершено! Обработано {total_updated} уникальных квартир")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)