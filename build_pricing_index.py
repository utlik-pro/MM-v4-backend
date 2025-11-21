#!/usr/bin/env python3
"""
Построение индекса цен для быстрого поиска квартир по бюджету
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any

class PricingIndexBuilder:
    def __init__(self):
        self.quarters_dir = Path("quarters")
        self.pricing_index = {
            "budget_categories": {
                "ultra_budget": {"range": [0, 50000], "quarters": [], "apartments": []},
                "budget": {"range": [50000, 70000], "quarters": [], "apartments": []},
                "affordable": {"range": [70000, 90000], "quarters": [], "apartments": []},
                "middle": {"range": [90000, 110000], "quarters": [], "apartments": []},
                "comfort": {"range": [110000, 140000], "quarters": [], "apartments": []},
                "premium": {"range": [140000, 170000], "quarters": [], "apartments": []},
                "luxury": {"range": [170000, 200000], "quarters": [], "apartments": []},
                "elite": {"range": [200000, 500000], "quarters": [], "apartments": []}
            },
            "priority_quarters": {
                "budget_first": [7, 21, 30],  # Приоритетные для бюджетных запросов
                "middle_first": [19, 26, 25, 23],
                "comfort_first": [29, 20, 12, 28, 18, 10],
                "premium_first": [11, 16, 27, 9, 22]
            },
            "quarters_info": {},
            "quarters_min_prices": {},
            "parking_spots": [],
            "cheapest_apartments": [],
            "statistics": {}
        }
        
    def extract_price_from_line(self, line: str) -> float:
        """Извлекает цену из строки"""
        # Паттерн для поиска цен в формате XXX,XXX евро или XXX евро
        price_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*евро'
        match = re.search(price_pattern, line)
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                return float(price_str)
            except:
                pass
        return None
    
    def parse_apartment_info(self, content: str, quarter_name: str) -> List[Dict]:
        """Парсит информацию о квартирах из файла квартала.
        Поддерживает заголовки с №/№№ и фильтрует статусы Продано/Резерв/Бронь.
        """
        apartments: List[Dict] = []
        lines = content.split('\n')

        def is_unavailable_status(text: str) -> bool:
            if not text:
                return False
            t = text.lower()
            blocked = ['продано', 'продан', 'sold', 'резерв', 'резервир', 'забронир', 'бронь']
            return any(b in t for b in blocked)

        current_apartment: Dict[str, Any] = {}
        current_unavailable = False

        for i, line in enumerate(lines):
            # Начало записи квартиры по признакам № и ключевых слов
            if re.search(r'№\s*№?\s*\d+', line) and re.search(r'(Квартира|Апартамент|апартаменты)', line, re.IGNORECASE):
                if current_apartment and 'price' in current_apartment and not current_unavailable:
                    apartments.append(current_apartment)
                m = re.search(r'№+\s*(\d+)', line)
                number = m.group(1) if m else 'unknown'
                current_apartment = {'quarter': quarter_name, 'number': number}
                current_unavailable = False

            if current_apartment and 'Площадь:' in line:
                am = re.search(r'(\d+\.?\d*)\s*м²', line)
                if am:
                    current_apartment['area'] = float(am.group(1))

            if current_apartment and 'Общая стоимость:' in line and 'рассрочку' not in line:
                price = self.extract_price_from_line(line)
                if price is not None:
                    current_apartment['price'] = price

            if current_apartment and re.search(r'\bЭтаж:\s*\d+', line):
                fm = re.search(r'Этаж:\s*(\d+)', line)
                if fm:
                    current_apartment['floor'] = int(fm.group(1))

            if current_apartment and ('Дом:' in line or 'Название дома:' in line):
                current_apartment['house'] = line.split(':', 1)[1].strip()

            if current_apartment and 'Статус:' in line:
                status_val = line.split(':', 1)[1].strip()
                current_apartment['status'] = status_val
                if is_unavailable_status(status_val):
                    current_unavailable = True

        if current_apartment and 'price' in current_apartment and not current_unavailable:
            apartments.append(current_apartment)

        # Ищем парковочные места
        parking_pattern = r'Парковочное место.*?(\d{1,3}(?:,\d{3})*)\s*евро'
        for match in re.finditer(parking_pattern, content, re.IGNORECASE):
            price_str = match.group(1).replace(',', '')
            try:
                price = float(price_str)
                self.pricing_index['parking_spots'].append({
                    'quarter': quarter_name,
                    'price': price,
                    'description': match.group(0)
                })
            except:
                pass
        
        # Фильтрация некорректных записей
        apartments = [a for a in apartments if a.get('quarter') and a.get('price')]
        return apartments
    
    def get_quarter_info(self, content: str, quarter_name: str) -> Dict:
        """Извлекает общую информацию о квартале"""
        info = {
            'name': quarter_name,
            'min_price': float('inf'),
            'max_price': 0,
            'avg_price': 0,
            'total_apartments': 0,
            'price_per_sqm': None
        }
        
        # Ищем цену за квадратный метр
        sqm_pattern = r'Цена за м²:\s*(\d{1,3}(?:,\d{3})*)\s*евро'
        sqm_match = re.search(sqm_pattern, content)
        if sqm_match:
            price_str = sqm_match.group(1).replace(',', '')
            try:
                info['price_per_sqm'] = float(price_str)
            except:
                pass
        
        return info
    
    def categorize_apartment(self, apartment: Dict):
        """Категоризирует квартиру по цене"""
        price = apartment['price']
        for category, data in self.pricing_index['budget_categories'].items():
            min_price, max_price = data['range']
            if min_price <= price < max_price:
                data['apartments'].append(apartment)
                
                # Добавляем квартал в список, если его еще нет
                quarter_num = self.extract_quarter_number(apartment['quarter'])
                if quarter_num and quarter_num not in data['quarters']:
                    data['quarters'].append(quarter_num)
                break
    
    def extract_quarter_number(self, quarter_name: str) -> int:
        """Извлекает номер квартала из имени файла"""
        match = re.match(r'^(\d+)-', quarter_name)
        if match:
            return int(match.group(1))
        return None
    
    def build_index(self):
        """Строит полный индекс цен"""
        all_apartments = []
        
        # Обрабатываем каждый файл квартала
        for md_file in self.quarters_dir.glob("*.md"):
            # Пропускаем служебные файлы
            if md_file.name.startswith("00-") or md_file.name.startswith("0"):
                continue
            
            quarter_name = md_file.stem
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Получаем информацию о квартале
                quarter_info = self.get_quarter_info(content, quarter_name)
                
                # Парсим квартиры
                apartments = self.parse_apartment_info(content, quarter_name)
                
                if apartments:
                    # Обновляем информацию о квартале
                    prices = [apt['price'] for apt in apartments]
                    quarter_info['min_price'] = min(prices)
                    quarter_info['max_price'] = max(prices)
                    quarter_info['avg_price'] = sum(prices) / len(prices)
                    quarter_info['total_apartments'] = len(apartments)
                    
                    self.pricing_index['quarters_info'][quarter_name] = quarter_info
                    # Сохраняем минимум по кварталу с метаданными
                    min_apartment = min(apartments, key=lambda x: x['price'])
                    self.pricing_index['quarters_min_prices'][quarter_name] = {
                        'min_price': min_apartment['price'],
                        'apartment': min_apartment
                    }
                    
                    # Категоризируем квартиры
                    for apartment in apartments:
                        self.categorize_apartment(apartment)
                        all_apartments.append(apartment)
                
            except Exception as e:
                print(f"Ошибка при обработке {md_file}: {e}")
        
        # Находим самые дешевые квартиры
        if all_apartments:
            all_apartments.sort(key=lambda x: x['price'])
            self.pricing_index['cheapest_apartments'] = all_apartments[:10]
            
            # Статистика
            all_prices = [apt['price'] for apt in all_apartments]
            self.pricing_index['statistics'] = {
                'total_apartments': len(all_apartments),
                'min_price': min(all_prices),
                'max_price': max(all_prices),
                'avg_price': sum(all_prices) / len(all_prices),
                'median_price': sorted(all_prices)[len(all_prices) // 2]
            }
        
        # Сортируем квартиры в категориях по цене
        for category_data in self.pricing_index['budget_categories'].values():
            category_data['apartments'].sort(key=lambda x: x['price'])
            category_data['quarters'].sort()
        
        # Сортируем парковочные места по цене
        self.pricing_index['parking_spots'].sort(key=lambda x: x['price'])
    
    def save_index(self, output_file: str = "pricing_index.json"):
        """Сохраняет индекс в JSON файл"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.pricing_index, f, ensure_ascii=False, indent=2)
        print(f"Индекс сохранен в {output_file}")
    
    def print_summary(self):
        """Выводит сводку по индексу"""
        print("\n📊 СВОДКА ПО ЦЕНОВОМУ ИНДЕКСУ")
        print("=" * 50)
        
        stats = self.pricing_index['statistics']
        if stats:
            print(f"Всего квартир: {stats['total_apartments']}")
            print(f"Минимальная цена: {stats['min_price']:,.0f} евро")
            print(f"Максимальная цена: {stats['max_price']:,.0f} евро")
            print(f"Средняя цена: {stats['avg_price']:,.0f} евро")
            print(f"Медианная цена: {stats['median_price']:,.0f} евро")
        
        print("\n💰 РАСПРЕДЕЛЕНИЕ ПО КАТЕГОРИЯМ:")
        for category, data in self.pricing_index['budget_categories'].items():
            count = len(data['apartments'])
            if count > 0:
                print(f"{category}: {count} квартир, кварталы: {data['quarters']}")
        
        print("\n🏆 ТОП-5 САМЫХ ДЕШЕВЫХ КВАРТИР:")
        for i, apt in enumerate(self.pricing_index['cheapest_apartments'][:5], 1):
            print(f"{i}. {apt['price']:,.0f} евро - Квартал {apt['quarter']}, "
                  f"№{apt.get('number', '?')}, {apt.get('area', '?')} м²")
        
        print("\n🅿️ ПАРКОВОЧНЫЕ МЕСТА:")
        if self.pricing_index['parking_spots']:
            print(f"Найдено {len(self.pricing_index['parking_spots'])} парковочных мест")
            print(f"Цены: от {self.pricing_index['parking_spots'][0]['price']:,.0f} "
                  f"до {self.pricing_index['parking_spots'][-1]['price']:,.0f} евро")


if __name__ == "__main__":
    builder = PricingIndexBuilder()
    print("🔨 Построение ценового индекса...")
    builder.build_index()
    builder.save_index()
    builder.print_summary()
    print("\n✅ Индекс успешно построен!")