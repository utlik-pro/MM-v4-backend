#!/usr/bin/env python3
"""
Скрипт для автоматического обновления поискового индекса квартир
Извлекает информацию из всех файлов квартир и создает структурированный индекс
"""

import os
import re
import glob
from pathlib import Path

def extract_apartment_info(content):
    """Извлекает информацию о квартирах из текста"""
    apartments = []
    
    # Паттерн для поиска квартир
    pattern = r'### 🏠 Квартира №№(\d+).*?\*\*Квартал:\*\* (.*?)\n\*\*Дом:\*\* (.*?)\n\*\*Название дома:\*\* (.*?)\n\*\*Этаж:\*\* (\d+)\n\*\*Общая этажность:\*\* (\d+)\n\*\*Площадь:\*\* ([\d.]+) м²\n\*\*Цена за м²:\*\* ([\d.]+) евро\n\*\*Общая стоимость:\*\* ([\d,]+\.?\d*) евро.*?\*\*Статус:\*\* (.*?)\n\*\*Адрес:\*\* (.*?)\n'
    
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        apartment = {
            'number': match.group(1),
            'quarter': match.group(2),
            'house': match.group(3),
            'house_name': match.group(4),
            'floor': int(match.group(5)),
            'total_floors': int(match.group(6)),
            'area': float(match.group(7)),
            'price_per_m2': float(match.group(8)),
            'total_price': float(match.group(9).replace(',', '')),
            'status': match.group(10),
            'address': match.group(11)
        }
        apartments.append(apartment)
    
    return apartments

def categorize_apartments(apartments):
    """Категоризирует квартиры по различным параметрам"""
    categories = {
        'by_area': {},
        'by_price': {},
        'by_status': {},
        'by_quarter': {},
        'ready_apartments': [],
        'under_construction': []
    }
    
    for apt in apartments:
        # По площади
        area_range = f"{int(apt['area']//10)*10}-{(int(apt['area']//10)*10)+10} м²"
        if area_range not in categories['by_area']:
            categories['by_area'][area_range] = []
        categories['by_area'][area_range].append(apt)
        
        # По цене
        price_range = f"{int(apt['total_price']//10000)*10000}-{(int(apt['total_price']//10000)*10000)+10000} евро"
        if price_range not in categories['by_price']:
            categories['by_price'][price_range] = []
        categories['by_price'][price_range].append(apt)
        
        # По статусу
        if 'готов' in apt['status'].lower() or 'сдано' in apt['status'].lower():
            categories['ready_apartments'].append(apt)
            categories['by_status']['ready'] = categories['by_status'].get('ready', []) + [apt]
        else:
            categories['under_construction'].append(apt)
            categories['by_status']['under_construction'] = categories['by_status'].get('under_construction', []) + [apt]
        
        # По кварталу
        if apt['quarter'] not in categories['by_quarter']:
            categories['by_quarter'][apt['quarter']] = []
        categories['by_quarter'][apt['quarter']].append(apt)
    
    return categories

def generate_search_index(categories):
    """Генерирует поисковый индекс в формате Markdown"""
    index_content = """# 🔍 Поисковый индекс квартир ЖК "Минск Мир"

## 📊 Готовые квартиры по площади

"""
    
    # Готовые квартиры по площади
    for area_range in sorted(categories['by_area'].keys()):
        ready_apts = [apt for apt in categories['by_area'][area_range] 
                     if apt in categories['ready_apartments']]
        if ready_apts:
            index_content += f"### {area_range}\n"
            for apt in ready_apts:
                index_content += f"- **Квартира №№{apt['number']} ({apt['house']})** - {apt['area']} м², {apt['total_price']:,.0f} евро, {apt['quarter']}, готово\n"
            index_content += "\n"
    
    index_content += "## 💰 Готовые квартиры по бюджету\n\n"
    
    # Готовые квартиры по цене
    for price_range in sorted(categories['by_price'].keys()):
        ready_apts = [apt for apt in categories['by_price'][price_range] 
                     if apt in categories['ready_apartments']]
        if ready_apts:
            index_content += f"### {price_range}\n"
            for apt in ready_apts:
                index_content += f"- **Квартира №№{apt['number']} ({apt['house']})** - {apt['area']} м², {apt['total_price']:,.0f} евро, {apt['quarter']}, готово\n"
            index_content += "\n"
    
    # Информация о метро
    index_content += """## 🚇 Квартиры рядом с метро

### Станция "Аэродромная"
- **Квартал 19 (Южная Европа)** - дома 19.6, 19.10
- **Квартал 25 (Азия)** - дома 25.1, 25.10
- **Квартал 22 (Центральная Европа)** - дом 22.7

## 🏠 Статус готовности

### ✅ Готовые квартиры (можно заселяться)
"""
    
    ready_quarters = set(apt['quarter'] for apt in categories['ready_apartments'])
    for quarter in sorted(ready_quarters):
        index_content += f"- {quarter} - все дома\n"
    
    index_content += "\n### 🏗️ Строящиеся квартиры\n"
    construction_quarters = set(apt['quarter'] for apt in categories['under_construction'])
    for quarter in sorted(construction_quarters):
        index_content += f"- {quarter} - все дома\n"
    
    # Быстрые команды поиска
    index_content += """
## 📋 Быстрые команды поиска

### Для агента:
- "Найти готовые квартиры 55-60 м² до 90,000 евро" → квартиры 25.10-3, 19.6-1, 19.6-4
- "Найти квартиры рядом с метро Аэродромная" → кварталы 19, 25
- "Найти готовые квартиры до 100,000 евро" → все квартиры в готовых кварталах
- "Найти квартиры с рассрочкой" → все квартиры с рассрочкой от застройщика
"""
    
    return index_content

def main():
    """Основная функция"""
    quarters_dir = Path("quarters")
    all_apartments = []
    
    # Сканируем все файлы квартир
    for file_path in quarters_dir.glob("*.md"):
        if file_path.name in ["README.md", "search_index.md", "00-obschie-svedeniya.md", 
                             "03-finansovye-uslugi.md", "04-baza-znaniy-dlya-konsultaciy.md", 
                             "05-sroki-sdachi-domov.md"]:
            continue
            
        print(f"Обрабатываю файл: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            apartments = extract_apartment_info(content)
            all_apartments.extend(apartments)
    
    print(f"Найдено квартир: {len(all_apartments)}")
    
    # Категоризируем квартиры
    categories = categorize_apartments(all_apartments)
    
    # Генерируем индекс
    index_content = generate_search_index(categories)
    
    # Сохраняем индекс
    index_path = quarters_dir / "search_index.md"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"Поисковый индекс обновлен: {index_path}")
    print(f"Готовых квартир: {len(categories['ready_apartments'])}")
    print(f"Строящихся квартир: {len(categories['under_construction'])}")

if __name__ == "__main__":
    main() 