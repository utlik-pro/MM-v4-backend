#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматическое обновление данных квартир из API bir.by
Использование:
  - Ручной запуск: python3 auto_update.py
  - Cron (каждый час): 0 * * * * cd /Users/admin/MM-RAG/quarters && python3 auto_update.py
  - С уведомлениями: python3 auto_update.py --notify
"""

import json
import re
import os
import sys
import hashlib
import logging
from datetime import datetime
from collections import defaultdict
import urllib.request
import argparse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/admin/MM-RAG/quarters/updates.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

def get_data_hash(data):
    """Получение хэша данных для проверки изменений"""
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()

def load_last_hash():
    """Загрузка последнего хэша"""
    hash_file = '/Users/admin/MM-RAG/quarters/.last_update_hash'
    if os.path.exists(hash_file):
        with open(hash_file, 'r') as f:
            return f.read().strip()
    return None

def save_hash(hash_value):
    """Сохранение хэша"""
    hash_file = '/Users/admin/MM-RAG/quarters/.last_update_hash'
    with open(hash_file, 'w') as f:
        f.write(hash_value)

def parse_existing_apartments(file_path):
    """Парсинг существующих квартир из MD файла"""
    apartments = []
    if not os.path.exists(file_path):
        return apartments
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    apartment_pattern = r'### 🏠 (Квартира|Пентхаус) №№?(\d+)'
    for match in re.finditer(apartment_pattern, content):
        apartments.append(f"{match.group(1)} №{match.group(2)}")
    
    return apartments

def generate_apartment_section(apartment):
    """Генерация секции для одной квартиры"""
    quarter_field = apartment.get('Quarter', '')
    if 'Квартал — ' in quarter_field:
        quarter_name = quarter_field.replace('Квартал — ', '').strip()
    else:
        quarter_name = ''
    
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
    content += "\n\n\n---\n\n"
    
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

            content += "\n\n\n---\n\n"
            
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
                    content += "\n\n\n---\n\n"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return len(apartments_data)

def main(notify=False, force=False):
    """Основная функция"""
    logger.info("=" * 50)
    logger.info("Запуск автоматического обновления")
    
    # Загрузка данных
    api_data = fetch_api_data()
    if not api_data:
        logger.error("Не удалось загрузить данные")
        return False
    
    # Проверка изменений
    current_hash = get_data_hash(api_data)
    last_hash = load_last_hash()
    
    if not force and current_hash == last_hash:
        logger.info("Данные не изменились с последнего обновления")
        return True
    
    # Маппинг кварталов
    quarter_mappings = {
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
        '29 Северная Европа': '29-Severnaya-Evropa.md',
        '30 Северная Америка': '30-Severnaya-Amerika.md',
        '02 Эмиратс': '02-emirats.md'
    }
    
    quarters_dir = '/Users/admin/MM-RAG/quarters'
    
    # Фильтрация и группировка
    quarters_data = defaultdict(list)
    valid_statuses = [
        'Статус: Сдано',
        'Статус: Строится',
        'Статус: Строящаяся квартира',
        'Статус: Строящиеся Бизнес-апартаменты'
    ]
    
    for key, apartment in api_data.items():
        status = apartment.get('Status', '')
        if not any(valid_status in status for valid_status in valid_statuses):
            continue
        
        quarter_field = apartment.get('Quarter', '')
        if 'Квартал — ' in quarter_field:
            quarter_name = quarter_field.replace('Квартал — ', '').strip()
            quarters_data[quarter_name].append(apartment)
        else:
            # Мапим по адресу для неизвестных
            house_number = apartment.get('NumberHouse', '')
            house_name = apartment.get('NameHouse', '')
            address = apartment.get('Address', '')
            
            if 'Эмиратс' in house_number or 'Эмиратс' in house_name or 'проспект Мира, дом 1' in address:
                quarters_data['02 Эмиратс'].append(apartment)
    
    # Обновление файлов
    changes = {}
    total_updated = 0
    
    for quarter_name, apartments in quarters_data.items():
        if quarter_name in quarter_mappings:
            file_name = quarter_mappings[quarter_name]
            file_path = os.path.join(quarters_dir, file_name)
            
            old_apartments = parse_existing_apartments(file_path)
            count = update_quarter_file(file_path, quarter_name, apartments)
            
            if len(old_apartments) != count:
                changes[quarter_name] = {
                    'old': len(old_apartments),
                    'new': count,
                    'diff': count - len(old_apartments)
                }
            
            total_updated += count
            logger.info(f"Обновлен {file_name}: {count} квартир")
    
    # Сохранение хэша
    save_hash(current_hash)
    
    # Генерация отчета об изменениях
    if changes:
        logger.info("=" * 50)
        logger.info("ОБНАРУЖЕНЫ ИЗМЕНЕНИЯ:")
        for quarter, info in changes.items():
            if info['diff'] > 0:
                logger.info(f"  📈 {quarter}: +{info['diff']} квартир (было {info['old']})")
            elif info['diff'] < 0:
                logger.info(f"  📉 {quarter}: {info['diff']} квартир (было {info['old']})")
        
        # Отправка уведомления
        if notify:
            send_notification(changes)
    
    logger.info(f"Обновление завершено. Всего квартир: {total_updated}")
    return True

def send_notification(changes):
    """Отправка уведомления об изменениях"""
    # Здесь можно добавить отправку в Telegram, Email и т.д.
    logger.info("Отправка уведомлений...")
    # TODO: Реализовать отправку

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Автоматическое обновление данных квартир')
    parser.add_argument('--notify', action='store_true', help='Отправлять уведомления об изменениях')
    parser.add_argument('--force', action='store_true', help='Принудительное обновление')
    args = parser.parse_args()
    
    success = main(notify=args.notify, force=args.force)
    sys.exit(0 if success else 1)