#!/usr/bin/env python3
"""
Улучшенная оптимизация парковочных мест с раздельной статистикой
"""

import re
from pathlib import Path

def analyze_and_optimize_quarter(file_path: str):
    """Анализирует и оптимизирует квартал с детальной статистикой"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n🔍 Анализирую {Path(file_path).name}...")
    
    # Подсчет по типам недвижимости
    business_apartments = len(re.findall(r'### 🏠 Бизнес-апартаменты', content))
    parking_spots = len(re.findall(r'### 🏠 Машиноместо', content))
    
    print(f"📊 Найдено:")
    print(f"   🏢 Бизнес-апартаментов: {business_apartments}")
    print(f"   🅿️ Машиноместов: {parking_spots}")
    
    if parking_spots == 0:
        print("   ✅ Машиноместа уже отсутствуют")
        return False
    
    # Анализ площадей и цен машиноместов
    parking_sections = re.findall(r'### 🏠 Машиноместо.*?---\n\n', content, re.DOTALL)
    
    areas = []
    prices = []
    house_names = set()
    
    for section in parking_sections:
        # Площадь
        area_match = re.search(r'\*\*Площадь:\*\* ([\d.]+) м²', section)
        if area_match:
            areas.append(float(area_match.group(1)))
        
        # Цена
        price_match = re.search(r'\*\*Общая стоимость:\*\* ([\d,.]+) евро', section)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            prices.append(float(price_str))
        
        # Название дома
        house_match = re.search(r'\*\*Название дома:\*\* (.+)', section)
        if house_match:
            house_names.add(house_match.group(1))
    
    # Анализ бизнес-апартаментов
    apartment_sections = re.findall(r'### 🏠 Бизнес-апартаменты.*?---\n\n', content, re.DOTALL)
    
    apt_areas = []
    apt_prices = []
    
    for section in apartment_sections:
        # Площадь
        area_match = re.search(r'\*\*Площадь:\*\* ([\d.]+) м²', section)
        if area_match:
            apt_areas.append(float(area_match.group(1)))
        
        # Цена
        price_match = re.search(r'\*\*Общая стоимость:\*\* ([\d,.]+) евро', section)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            apt_prices.append(float(price_str))
    
    print(f"   📐 Площади машиноместов: {min(areas):.1f} - {max(areas):.1f} м² (средняя: {sum(areas)/len(areas):.1f})")
    print(f"   💰 Стоимость машиноместов: {min(prices):,.0f} - {max(prices):,.0f} евро (средняя: {sum(prices)/len(prices):,.0f})")
    print(f"   🏠 Дома с парковкой: {', '.join(house_names)}")
    
    if apt_areas:
        print(f"   📐 Площади апартаментов: {min(apt_areas):.1f} - {max(apt_areas):.1f} м² (средняя: {sum(apt_areas)/len(apt_areas):.1f})")
        print(f"   💰 Стоимость апартаментов: {min(apt_prices):,.0f} - {max(apt_prices):,.0f} евро (средняя: {sum(apt_prices)/len(apt_prices):,.0f})")
    
    # Создание улучшенной сводки
    parking_summary = f"""## 🅿️ Парковочные места
**Дома с парковкой:** {', '.join(house_names)}  
**Количество:** {parking_spots} машиномест  
**Площадь:** от {min(areas):.1f} до {max(areas):.1f} м² (средняя {sum(areas)/len(areas):.1f} м²)  
**Стоимость:** от {min(prices):,.0f} до {max(prices):,.0f} евро (средняя {sum(prices)/len(prices):,.0f} евро)  
**Наличие:** Доступны парковочные места различных размеров

## 🏢 Статистика по типам недвижимости
**Бизнес-апартаменты:** {business_apartments} объектов"""

    if apt_areas:
        parking_summary += f"""  
- Площадь: от {min(apt_areas):.1f} до {max(apt_areas):.1f} м² (средняя {sum(apt_areas)/len(apt_areas):.1f} м²)  
- Стоимость: от {min(apt_prices):,.0f} до {max(apt_prices):,.0f} евро (средняя {sum(apt_prices)/len(apt_prices):,.0f} евро)"""

    parking_summary += f"""

**Машиноместа:** {parking_spots} объектов  
- Площадь: от {min(areas):.1f} до {max(areas):.1f} м² (средняя {sum(areas)/len(areas):.1f} м²)  
- Стоимость: от {min(prices):,.0f} до {max(prices):,.0f} евро (средняя {sum(prices)/len(prices):,.0f} евро)"""
    
    # Удаляем все машиноместа
    original_size = len(content)
    content = re.sub(r'### 🏠 Машиноместо.*?---\n\n', '', content, flags=re.DOTALL)
    
    # Обновляем типы недвижимости
    content = re.sub(r'Бизнес-апартаменты, Машиноместо', 'Бизнес-апартаменты', content)
    
    # Добавляем улучшенную сводку
    info_pattern = r'(\*\*Типы недвижимости:\*\*[^\n]*\n\n---\n\n)'
    replacement = r'\1' + parking_summary + '\n\n---\n\n'
    content = re.sub(info_pattern, replacement, content)
    
    # Очистка лишних переносов
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Сохранение файла
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_size = len(content)
    saved_kb = (original_size - new_size) / 1024
    
    print(f"   ✅ Удалено {parking_spots} машиномест")
    print(f"   📊 Размер: {original_size:,} → {new_size:,} байт (-{saved_kb:.1f} КБ)")
    print(f"   📈 Добавлена детальная статистика по типам недвижимости")
    
    return True

def main():
    """Основная функция"""
    print("🅿️ Улучшенная оптимизация парковочных мест (версия 2.0)")
    print("=" * 65)
    
    file_path = "quarters/21-Zapadnyy.md"
    
    if Path(file_path).exists():
        analyze_and_optimize_quarter(file_path)
        print("\n🎉 Оптимизация завершена!")
    else:
        print(f"❌ Файл не найден: {file_path}")

if __name__ == "__main__":
    main()
