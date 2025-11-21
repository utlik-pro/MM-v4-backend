#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер данных недвижимости с bir.by для RAG агента 11labs
Версия без машиномест - только жилая и коммерческая недвижимость
"""

import json
import requests
import unicodedata
import re
from collections import defaultdict
from typing import Dict, List, Any
import os

class BirDataParserNoParking:
    def __init__(self, json_url: str = "https://bir.by/ai/json_ai.php"):
        self.json_url = json_url
        self.data = None
        self.quarters = defaultdict(lambda: defaultdict(list))
        self.excluded_count = 0
        
    def fetch_data(self) -> bool:
        """Загружает JSON данные с сайта"""
        try:
            response = requests.get(self.json_url, timeout=30)
            response.raise_for_status()
            self.data = response.json()
            return True
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            return False
    
    def decode_unicode(self, text: str) -> str:
        """Декодирует Unicode последовательности в читаемый текст"""
        if not text:
            return ""
        
        # Если текст уже нормальный, возвращаем как есть
        if not text.startswith('\\u'):
            return text
        
        try:
            # Декодируем Unicode escape sequences
            decoded = text.encode('utf-8').decode('unicode_escape')
            return decoded
        except:
            try:
                # Альтернативный способ декодирования
                return text.encode('latin1').decode('utf-8')
            except:
                try:
                    # Еще один способ - через bytes
                    return bytes(text, 'utf-8').decode('unicode_escape')
                except:
                    return text
    
    def is_parking_space(self, item: Dict) -> bool:
        """Проверяет, является ли объект машиноместом"""
        # Проверяем по типу
        item_type = self.decode_unicode(item.get('type', '')).lower()
        if 'машиноместо' in item_type or 'паркинг' in item_type or 'parking' in item_type:
            return True
        
        # Проверяем по названию
        apartment_name = self.decode_unicode(item.get('Apartment', '')).lower()
        if 'машиноместо' in apartment_name or 'паркинг' in apartment_name:
            return True
        
        # Проверяем по названию дома
        house_name = self.decode_unicode(item.get('NameHouse', '')).lower()
        if 'паркинг' in house_name:
            return True
        
        # Дополнительная проверка по маленькой площади (типично для парковок)
        square = self.extract_square(item.get('Square', ''))
        if square > 0 and square < 20:  # Обычно машиноместа меньше 20 м²
            # Но нужно убедиться что это не маленькая квартира-студия
            if 'квартира' not in apartment_name and 'апартамент' not in apartment_name:
                # Проверяем цену - у машиномест обычно низкая цена
                price = self.safe_float(item.get('Price_full', 0))
                if price > 0 and price < 25000:  # Машиноместа обычно стоят меньше 25000
                    return True
        
        return False
    
    def extract_quarter_name(self, quarter_text: str) -> str:
        """Извлекает название квартала из текста"""
        if not quarter_text:
            return "Неизвестный квартал"
        
        decoded = self.decode_unicode(quarter_text)
        
        # Если текст пустой или содержит только пробелы
        if not decoded.strip():
            return "Неизвестный квартал"
        
        # Ищем паттерн "Квартал — [название]"
        match = re.search(r'Квартал\s*[—\-]\s*(.+)', decoded)
        if match:
            quarter_name = match.group(1).strip()
            if quarter_name:  # Проверяем, что название не пустое
                return quarter_name
        
        # Если не нашли паттерн, попробуем извлечь номер квартала
        match = re.search(r'(\d+)\s*[—\-]\s*(.+)', decoded)
        if match:
            quarter_name = f"Квартал {match.group(1)} {match.group(2).strip()}"
            if quarter_name and quarter_name != "Квартал  ":
                return quarter_name
        
        # Если текст содержит только цифры или специальные символы
        if re.match(r'^[\d\s\-—]+$', decoded.strip()):
            return "Неизвестный квартал"
        
        # Если текст слишком короткий или подозрительный
        if len(decoded.strip()) < 3:
            return "Неизвестный квартал"
        
        # Если текст содержит только служебные символы
        if re.match(r'^[^\wа-яё]+$', decoded.strip(), re.IGNORECASE):
            return "Неизвестный квартал"
        
        # Если все проверки пройдены, возвращаем очищенный текст
        cleaned = decoded.strip()
        if cleaned:
            return cleaned
        
        return "Неизвестный квартал"
    
    def extract_house_number(self, house_text: str) -> str:
        """Извлекает номер дома"""
        if not house_text:
            return "Неизвестный дом"
        
        decoded = self.decode_unicode(house_text)
        # Ищем цифры в названии дома
        match = re.search(r'(\d+(?:\.\d+)?)', decoded)
        if match:
            return match.group(1)
        return decoded.strip()
    
    def extract_floor_number(self, floor_text: str) -> int:
        """Извлекает номер этажа"""
        if not floor_text:
            return 0
        
        decoded = self.decode_unicode(floor_text)
        # Ищем цифры в тексте этажа
        match = re.search(r'(\d+)', decoded)
        if match:
            return int(match.group(1))
        return 0
    
    def extract_square(self, square_text: str) -> float:
        """Извлекает площадь из текста"""
        if not square_text:
            return 0.0
        
        decoded = self.decode_unicode(square_text)
        # Ищем число с плавающей точкой
        match = re.search(r'(\d+(?:\.\d+)?)', decoded)
        if match:
            return float(match.group(1))
        return 0.0
    
    def safe_float(self, value) -> float:
        """Безопасно конвертирует значение в float"""
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Убираем все нечисловые символы кроме точки и минуса
            cleaned = re.sub(r'[^\d.-]', '', value)
            try:
                return float(cleaned) if cleaned else 0.0
            except ValueError:
                return 0.0
        return 0.0
    
    def parse_data(self):
        """Парсит и структурирует данные, исключая машиноместа"""
        if not self.data:
            print("Данные не загружены")
            return
        
        total_items = len(self.data)
        filtered_items = 0
        
        for item_id, item in self.data.items():
            # Пропускаем машиноместа
            if self.is_parking_space(item):
                self.excluded_count += 1
                continue
            
            filtered_items += 1
            
            # Декодируем все текстовые поля
            quarter = self.extract_quarter_name(item.get('Quarter', ''))
            house_number = self.extract_house_number(item.get('NumberHouse', ''))
            house_name = self.decode_unicode(item.get('NameHouse', ''))
            floor = self.extract_floor_number(item.get('Floor', ''))
            square = self.extract_square(item.get('Square', ''))
            address = self.decode_unicode(item.get('Address', ''))
            
            # Если квартал неизвестный, пытаемся определить по адресу
            if quarter == "Неизвестный квартал":
                quarter = self.determine_quarter_by_address(address, house_name, house_number)
            
            # Создаем структурированный объект
            structured_item = {
                'id': item_id,
                'apartment': self.decode_unicode(item.get('Apartment', '')),
                'type': self.decode_unicode(item.get('type', '')),
                'quarter': quarter,
                'house_number': house_number,
                'house_name': house_name,
                'floor': floor,
                'floor_total': self.extract_floor_number(item.get('FloorTotal', '')),
                'square': square,
                'status': self.decode_unicode(item.get('Status', '')),
                'address': address,
                'location': self.decode_unicode(item.get('Location', '')),
                'price_metr': self.safe_float(item.get('Price_metr', 0)),
                'price_full': self.safe_float(item.get('Price_full', 0)),
                'installment_price_metr': self.safe_float(item.get('Installment_price_metr', 0)),
                'installment_price_full': self.safe_float(item.get('Installment_price_full', 0))
            }
            
            # Группируем по кварталам и домам
            self.quarters[quarter][house_number].append(structured_item)
        
        print(f"📊 Фильтрация: из {total_items} объектов отфильтровано {filtered_items}")
        print(f"🚗 Исключено машиномест: {self.excluded_count}")
    
    def generate_quarter_markdown(self, quarter_name: str, houses: Dict) -> str:
        """Генерирует Markdown для квартала"""
        markdown = f"# 🏘️ Квартал — {quarter_name}\n\n"
        
        # Общая информация
        total_objects = sum(len(apartments) for apartments in houses.values())
        unique_types = set()
        for house_apartments in houses.values():
            for apt in house_apartments:
                unique_types.add(apt['type'])
        
        markdown += "## 📍 Общая информация\n"
        markdown += f"**Квартал:** {quarter_name}\n"
        markdown += f"**Город:** Минск\n"
        markdown += f"**Район:** Мир\n"
        markdown += f"**Количество домов:** {len(houses)}\n"
        markdown += f"**Количество объектов:** {total_objects}\n"
        markdown += f"**Типы недвижимости:** {', '.join(unique_types)}\n\n"
        markdown += "---\n\n"
        
        # Статистика по кварталу
        all_prices = []
        all_squares = []
        all_costs = []
        
        for house_number, apartments in houses.items():
            for apt in apartments:
                if apt['price_metr'] > 0:
                    all_prices.append(apt['price_metr'])
                if apt['square'] > 0:
                    all_squares.append(apt['square'])
                if apt['price_full'] > 0:
                    all_costs.append(apt['price_full'])
        
        # Генерируем информацию по каждому дому
        for house_number, apartments in houses.items():
            markdown += self.generate_house_markdown(house_number, apartments)
        
        # Аналитика квартала
        if all_prices or all_squares or all_costs:
            markdown += self.generate_quarter_analytics(all_prices, all_squares, all_costs)
        
        return markdown
    
    def generate_house_markdown(self, house_number: str, apartments: List[Dict]) -> str:
        """Генерирует Markdown для дома"""
        if not apartments:
            return ""
        
        house_name = apartments[0].get('house_name', '')
        markdown = f"## 🏠 Дом {house_number}\n\n"
        
        if house_name:
            markdown += f"**Название дома:** {house_name}\n\n"
        
        # Статистика дома
        prices = [apt['price_metr'] for apt in apartments if apt['price_metr'] > 0]
        squares = [apt['square'] for apt in apartments if apt['square'] > 0]
        costs = [apt['price_full'] for apt in apartments if apt['price_full'] > 0]
        
        markdown += "### 📊 Статистика дома\n"
        markdown += f"**Количество апартаментов:** {len(apartments)}\n"
        if squares:
            markdown += f"**Диапазон площадей:** {min(squares):.1f} - {max(squares):.1f} м²\n"
        if prices:
            markdown += f"**Средняя цена за м²:** {sum(prices)/len(prices):.0f} евро\n"
        if costs:
            markdown += f"**Средняя стоимость:** {sum(costs)/len(costs):.0f} евро\n"
        markdown += "\n---\n\n"
        
        # Группируем по этажам
        floors = defaultdict(list)
        for apt in apartments:
            floors[apt['floor']].append(apt)
        
        # Генерируем информацию по этажам
        for floor_num in sorted(floors.keys()):
            markdown += f"## 🏢 Этаж {floor_num}\n\n"
            for apt in floors[floor_num]:
                markdown += self.generate_apartment_markdown(apt)
            markdown += "\n"
        
        return markdown
    
    def generate_apartment_markdown(self, apartment: Dict) -> str:
        """Генерирует Markdown для апартамента"""
        markdown = f"### 🏠 {apartment['type']} №{apartment['apartment'].split()[-1] if apartment['apartment'] else 'N/A'}\n"
        markdown += f"**Квартал:** {apartment['quarter']}\n"
        markdown += f"**Дом:** {apartment['house_number']}\n"
        if apartment['house_name']:
            markdown += f"**Название дома:** {apartment['house_name']}\n"
        markdown += f"**Этаж:** {apartment['floor']}\n"
        if apartment['floor_total'] > 0:
            markdown += f"**Общая этажность:** {apartment['floor_total']}\n"
        if apartment['square'] > 0:
            markdown += f"**Площадь:** {apartment['square']} м²\n"
        if apartment['price_metr'] > 0:
            markdown += f"**Цена за м²:** {apartment['price_metr']} евро\n"
        if apartment['price_full'] > 0:
            markdown += f"**Общая стоимость:** {apartment['price_full']:,} евро\n"
        if apartment['installment_price_metr'] > 0:
            markdown += f"**Цена в рассрочку за м²:** {apartment['installment_price_metr']} евро\n"
        if apartment['installment_price_full'] > 0:
            markdown += f"**Общая стоимость в рассрочку:** {apartment['installment_price_full']:,} евро\n"
        if apartment['status']:
            markdown += f"**Статус:** {apartment['status']}\n"
        if apartment['address']:
            markdown += f"**Адрес:** {apartment['address']}\n"
        if apartment['location']:
            markdown += f"**Местоположение:** {apartment['location']}\n"
        markdown += "\n---\n\n"
        
        return markdown
    
    def generate_quarter_analytics(self, prices: List[float], squares: List[float], costs: List[float]) -> str:
        """Генерирует аналитику квартала"""
        markdown = "## 📈 Аналитика квартала\n\n"
        
        if prices:
            markdown += "### 💰 Ценовой диапазон\n"
            markdown += f"- **Минимальная цена за м²:** {min(prices):.0f} евро\n"
            markdown += f"- **Максимальная цена за м²:** {max(prices):.0f} евро\n"
            markdown += f"- **Средняя цена за м²:** {sum(prices)/len(prices):.0f} евро\n\n"
        
        if squares:
            markdown += "### 📐 Площади\n"
            markdown += f"- **Минимальная площадь:** {min(squares):.1f} м²\n"
            markdown += f"- **Максимальная площадь:** {max(squares):.1f} м²\n"
            markdown += f"- **Средняя площадь:** {sum(squares)/len(squares):.1f} м²\n\n"
        
        if costs:
            markdown += "### 💵 Стоимость\n"
            markdown += f"- **Минимальная стоимость:** {min(costs):,.0f} евро\n"
            markdown += f"- **Максимальная стоимость:** {max(costs):,.0f} евро\n"
            markdown += f"- **Средняя стоимость:** {sum(costs)/len(costs):,.0f} евро\n\n"
        
        markdown += "---\n\n"
        return markdown
    
    def save_quarter_files(self, output_dir: str = "quarters"):
        """Сохраняет файлы для каждого квартала"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for quarter_name, houses in self.quarters.items():
            # Создаем безопасное имя файла с транслитерацией
            safe_name = self.create_safe_filename(quarter_name)
            filename = f"{safe_name}.md"
            filepath = os.path.join(output_dir, filename)
            
            markdown_content = self.generate_quarter_markdown(quarter_name, houses)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Создан файл: {filepath}")
    
    def create_safe_filename(self, text: str) -> str:
        """Создает безопасное имя файла с транслитерацией кириллицы"""
        # Словарь для транслитерации кириллицы
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
            ' ': '-', '-': '-', '_': '-'
        }
        
        # Транслитерируем текст
        result = ""
        for char in text:
            if char in translit_dict:
                result += translit_dict[char]
            elif char.isalnum():
                result += char
            else:
                result += '-'
        
        # Убираем множественные дефисы и дефисы в начале/конце
        result = re.sub(r'-+', '-', result)
        result = result.strip('-')
        
        # Если результат пустой, используем fallback
        if not result:
            result = "quarter"
        
        return result
    
    def generate_index_file(self, output_dir: str = "quarters"):
        """Создает индексный файл со списком всех кварталов"""
        index_content = "# 🏘️ Индекс кварталов недвижимости (без машиномест)\n\n"
        index_content += "## 📋 Список доступных кварталов\n\n"
        
        for quarter_name in sorted(self.quarters.keys()):
            safe_name = self.create_safe_filename(quarter_name)
            filename = f"{safe_name}.md"
            
            total_objects = sum(len(apartments) for apartments in self.quarters[quarter_name].values())
            index_content += f"- [{quarter_name}]({filename}) - {total_objects} объектов\n"
        
        index_content += "\n---\n\n"
        index_content += "## 📊 Общая статистика\n\n"
        
        total_quarters = len(self.quarters)
        total_houses = sum(len(houses) for houses in self.quarters.values())
        total_objects = sum(len(apartments) for houses in self.quarters.values() for apartments in houses.values())
        
        index_content += f"- **Всего кварталов:** {total_quarters}\n"
        index_content += f"- **Всего домов:** {total_houses}\n"
        index_content += f"- **Всего объектов (без машиномест):** {total_objects}\n"
        index_content += f"- **Исключено машиномест:** {self.excluded_count}\n"
        
        index_path = os.path.join(output_dir, "README.md")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"Создан индексный файл: {index_path}")

    def determine_quarter_by_address(self, address: str, house_name: str, house_number: str) -> str:
        """Определяет квартал по адресу и названию дома"""
        if not address:
            return "Неизвестный квартал"
        
        address_lower = address.lower()
        house_name_lower = house_name.lower() if house_name else ""
        
        # Анализируем адреса и определяем кварталы
        if "проспект мира" in address_lower:
            if "дом 1" in address_lower:
                # Все объекты на проспекте Мира, дом 1 относятся к кварталу 9 Южная Америка
                return "9 Южная Америка"
            elif "дом 2" in address_lower:
                return "9 Южная Америка"
        
        elif "улица германовская" in address_lower:
            return "9 Южная Америка"
        
        elif "улица леонида левина" in address_lower:
            return "9 Южная Америка"
        
        elif "улица игоря лученка" in address_lower:
            return "9 Южная Америка"
        
        elif "ул. аэродромная" in address_lower:
            return "9 Южная Америка"
        
        elif "ул. братская" in address_lower:
            return "9 Южная Америка"
        
        elif "ул. белградская" in address_lower:
            return "9 Южная Америка"
        
        # Если не удалось определить, возвращаем неизвестный
        return "Неизвестный квартал"

def main():
    """Основная функция"""
    print("🏘️ Парсер данных недвижимости BIR.BY (без машиномест)")
    print("=" * 50)
    
    parser = BirDataParserNoParking()
    
    # Загружаем данные
    print("📥 Загрузка данных...")
    if not parser.fetch_data():
        print("❌ Не удалось загрузить данные")
        return
    
    print(f"✅ Загружено {len(parser.data)} объектов")
    
    # Парсим данные
    print("🔍 Парсинг данных и фильтрация машиномест...")
    parser.parse_data()
    
    print(f"✅ Обработано {len(parser.quarters)} кварталов")
    
    # Показываем статистику по кварталам
    print("\n📊 Статистика по кварталам (без машиномест):")
    for quarter_name, houses in parser.quarters.items():
        total_objects = sum(len(apartments) for apartments in houses.values())
        print(f"  {quarter_name}: {total_objects} объектов")
    
    # Сохраняем файлы
    print("\n💾 Сохранение файлов...")
    parser.save_quarter_files()
    parser.generate_index_file()
    
    print("✅ Готово! Файлы сохранены в папке 'quarters'")

if __name__ == "__main__":
    main()