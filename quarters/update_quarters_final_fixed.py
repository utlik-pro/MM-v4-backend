#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная версия скрипта обновления с учетом всех правил
Правила:
1. Диадема - всегда квартал 02 Эмиратс (только 2 квартиры)
2. Эмиратс Волна - название дома Волна (НЕ Диадема!)
"""

import json
import re
import os
import sys
import logging
from datetime import datetime
from collections import defaultdict, Counter
import urllib.request

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """Загрузка конфигурации правил"""
    config_path = '/Users/admin/MM-RAG/quarters/config_rules.json'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def fetch_api_data():
    """Загрузка данных из API"""
    api_url = 'https://bir.by/ai/json_ai.php'
    try:
        with urllib.request.urlopen(api_url, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        logger.error(f"Ошибка API: {e}")
        return None

def fix_house_name(apartment):
    """Исправление названия дома согласно правилам"""
    house_number = apartment.get('NumberHouse', '')
    current_name = apartment.get('NameHouse', '')
    
    # Правило: Эмиратс Волна -> название дома Волна
    if 'Эмиратс Волна' in house_number:
        apartment['NameHouse'] = 'Волна'
        logger.debug(f"Исправлено: {house_number} -> Волна")
    
    # Правило: Диадема остается Диадемой только для специфичных домов
    # Но НЕ для Эмиратс Волна
    if house_number == 'Диадема' or ('Диадема' in current_name and 'Волна' not in house_number):
        apartment['NameHouse'] = 'Диадема'
    
    return apartment

def determine_quarter(apartment):
    """Определение квартала с учетом правил"""
    # 1. Проверяем явно указанный квартал
    quarter_field = apartment.get('Quarter', '')
    if 'Квартал — ' in quarter_field:
        return quarter_field.replace('Квартал — ', '').strip()
    
    house_name = apartment.get('NameHouse', '')
    house_number = apartment.get('NumberHouse', '')
    address = apartment.get('Address', '')
    
    # 2. Правило для Диадемы
    if 'Диадема' in house_name or house_number == 'Диадема':
        return '02 Эмиратс'
    
    # 3. Правило для Эмиратс Волна
    if 'Эмиратс Волна' in house_number:
        return '02 Эмиратс'
    
    # 4. Проверка по адресу
    if 'проспект Мира, дом 1' in address:
        return '02 Эмиратс'
    
    return None

def generate_apartment_section(apartment):
    """Генерация секции для квартиры"""
    quarter_field = apartment.get('Quarter', '')
    if 'Квартал — ' in quarter_field:
        quarter_name = quarter_field.replace('Квартал — ', '').strip()
    else:
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
    # Если нет квартир - создаем файл с информацией об отсутствии
    if not apartments_data:
        content = f"# 🏘️ Квартал — {quarter_name}\n\n"
        content += f"## 📍 Общая информация\n"
        content += f"**Квартал:** {quarter_name}\n"
        content += f"**Город:** Минск\n"
        content += f"**Район:** Мир\n"
        content += f"**Количество домов:** 0\n"
        content += f"**Количество объектов:** 0\n"
        content += f"**Типы недвижимости:** -\n"
        content += f"**Обновлено:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        content += f"## 📊 Статус квартала\n\n"
        content += f"**🚫 В данный момент нет доступных квартир для продажи**\n\n"
        content += f"Все квартиры в квартале {quarter_name} проданы или забронированы.\n\n"
        content += f"---\n\n"
        content += f"## 📞 Контакты\n\n"
        content += f"Для получения информации о будущих объектах в этом квартале, пожалуйста, свяжитесь с отделом продаж.\n\n"
        content += "/n/n\n---"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return 0
    
    houses = defaultdict(lambda: defaultdict(list))
    
    for apt in apartments_data:
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
    content += f"**Количество объектов:** {len(apartments_data)}\n"
    
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
    
    return len(apartments_data)

def main():
    """Основная функция"""
    print("\n" + "="*70)
    print("🚀 ЗАПУСК ОБНОВЛЕНИЯ С ПРАВИЛАМИ")
    print("="*70)
    print("📄 Правила:")
    print("  1. Диадема - всегда квартал 02 Эмиратс (только 2 квартиры)")
    print("  2. Эмиратс Волна - название дома Волна (НЕ Диадема!)")
    print("="*70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Загрузка конфигурации
    config = load_config()
    if not config:
        logger.warning("Конфигурация не найдена, используются встроенные правила")
    
    # Загрузка данных
    api_data = fetch_api_data()
    if not api_data:
        print("❌ Не удалось загрузить данные")
        return False
    
    print(f"📊 Загружено объектов: {len(api_data)}")
    
    # Маппинг кварталов
    quarter_mappings = config.get('quarter_mappings', {}) if config else {
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
        '28 Happy Planet': '28-Happy-Planet.md',  # Добавляем квартал 28
        '29 Северная Европа': '29-Severnaya-Evropa.md',
        '30 Северная Америка': '30-Severnaya-Amerika.md',
        '02 Эмиратс': '02-emirats.md'
    }
    
    valid_statuses = config.get('valid_statuses', []) if config else [
        'Статус: Сдано',
        'Статус: Строится',
        'Статус: Строящаяся квартира',
        'Статус: Строящиеся Бизнес-апартаменты'
    ]
    
    # Группировка и фильтрация
    quarters_data = defaultdict(list)
    unknown_quarters = []
    filtered_count = 0
    diadema_count = 0
    volna_count = 0
    
    for key, apartment in api_data.items():
        status = apartment.get('Status', '')
        
        # Проверяем статус
        if not any(valid_status in status for valid_status in valid_statuses):
            filtered_count += 1
            continue
        
        # Исправляем название дома
        apartment = fix_house_name(apartment)
        
        # Определяем квартал
        quarter_name = determine_quarter(apartment)
        
        if quarter_name:
            quarters_data[quarter_name].append(apartment)
            
            # Считаем Диадему и Волну
            if apartment.get('NameHouse') == 'Диадема':
                diadema_count += 1
            elif apartment.get('NameHouse') == 'Волна':
                volna_count += 1
        else:
            unknown_quarters.append(apartment)
    
    print(f"📊 Отфильтровано (проданы/забронированы): {filtered_count}")
    print(f"🏠 Квартир в доме Диадема: {diadema_count}")
    print(f"🌊 Квартир в доме Волна: {volna_count}")
    
    if unknown_quarters:
        print(f"\n⚠️  Квартир без определенного квартала: {len(unknown_quarters)}")
        for apt in unknown_quarters[:3]:
            print(f"   - {apt.get('Apartment')} | Дом: {apt.get('NumberHouse')} | Адрес: {apt.get('Address')}")
    
    # Распределение по кварталам
    print("\n📊 Распределение квартир по кварталам:")
    for quarter_name, apartments in sorted(quarters_data.items()):
        print(f"  {quarter_name}: {len(apartments)} квартир")
    
    # Обновление файлов
    quarters_dir = '/Users/admin/MM-RAG/quarters'
    total_updated = 0
    
    print("\n📝 Обновление файлов...")
    for quarter_name, apartments in quarters_data.items():
        if quarter_name in quarter_mappings:
            file_name = quarter_mappings[quarter_name]
            file_path = os.path.join(quarters_dir, file_name)
            
            count = update_quarter_file(file_path, quarter_name, apartments)
            total_updated += count
            
            print(f"  ✅ {file_name}: {count} квартир")
    
    print("\n" + "="*70)
    print(f"✅ Обновление завершено! Обработано {total_updated} квартир")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)