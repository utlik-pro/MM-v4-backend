#!/usr/bin/env python3
"""
Конвертер Markdown файлов в JSON формат для базы знаний MM-RAG
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any
import argparse
from datetime import datetime


class MDtoJSONConverter:
    """Класс для конвертации MD файлов в структурированный JSON"""
    
    def __init__(self):
        self.properties = []
        
    def parse_md_file(self, file_path: str) -> Dict[str, Any]:
        """Парсинг MD файла в структурированный словарь"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Основная информация о квартале
        quarter_info = {}
        quarter_match = re.search(r'\*\*Квартал:\*\* (.+)', content)
        if quarter_match:
            quarter_info['quarter'] = quarter_match.group(1)
        
        city_match = re.search(r'\*\*Город:\*\* (.+)', content)
        if city_match:
            quarter_info['city'] = city_match.group(1)
        
        district_match = re.search(r'\*\*Район:\*\* (.+)', content)
        if district_match:
            quarter_info['district'] = district_match.group(1)
        
        # Парсинг домов и квартир
        buildings = []
        building_sections = re.split(r'## 🏠 Дом', content)[1:]
        
        for building_section in building_sections:
            building = self.parse_building(building_section, quarter_info)
            if building:
                buildings.append(building)
        
        # Формируем результирующую структуру
        file_name = os.path.basename(file_path)
        property_id = file_name.split('-')[0] if '-' in file_name else '00'
        
        return {
            'id': property_id,
            'source_file': file_name,
            'quarter': quarter_info.get('quarter', ''),
            'city': quarter_info.get('city', ''),
            'district': quarter_info.get('district', ''),
            'buildings': buildings
        }
    
    def parse_building(self, section: str, quarter_info: Dict) -> Dict[str, Any]:
        """Парсинг информации о доме"""
        lines = section.strip().split('\n')
        if not lines:
            return None
        
        # Название дома
        building_name = lines[0].strip()
        
        building = {
            'name': building_name,
            'apartments': []
        }
        
        # Парсим статистику дома
        stats_match = re.search(r'\*\*Количество апартаментов:\*\* (\d+)', section)
        if stats_match:
            building['total_apartments'] = int(stats_match.group(1))
        
        area_match = re.search(r'\*\*Диапазон площадей:\*\* ([\d\.]+) - ([\d\.]+)', section)
        if area_match:
            building['area_range'] = {
                'min': float(area_match.group(1)),
                'max': float(area_match.group(2))
            }
        
        avg_price_match = re.search(r'\*\*Средняя цена за м²:\*\* ([\d\.]+)', section)
        if avg_price_match:
            building['avg_price_per_sqm'] = float(avg_price_match.group(1))
        
        # Парсим квартиры
        apartment_sections = re.split(r'### 🏠 Квартира', section)[1:]
        
        for apt_section in apartment_sections:
            apartment = self.parse_apartment(apt_section)
            if apartment:
                apartment['building'] = building_name
                apartment['quarter'] = quarter_info.get('quarter', '')
                apartment['city'] = quarter_info.get('city', '')
                apartment['district'] = quarter_info.get('district', '')
                building['apartments'].append(apartment)
        
        return building
    
    def parse_apartment(self, section: str) -> Dict[str, Any]:
        """Парсинг информации о квартире"""
        apartment = {}
        
        # Номер квартиры
        number_match = re.search(r'№№(\d+)', section)
        if number_match:
            apartment['number'] = number_match.group(1)
        
        # Этаж
        floor_match = re.search(r'\*\*Этаж:\*\* (\d+)', section)
        if floor_match:
            apartment['floor'] = int(floor_match.group(1))
        
        # Площадь
        area_match = re.search(r'\*\*Площадь:\*\* ([\d\.]+)', section)
        if area_match:
            apartment['area'] = float(area_match.group(1))
        
        # Цена за м²
        price_sqm_match = re.search(r'\*\*Цена за м²:\*\* ([\d\.]+)', section)
        if price_sqm_match:
            apartment['price_per_sqm'] = float(price_sqm_match.group(1))
        
        # Общая стоимость
        total_match = re.search(r'\*\*Общая стоимость:\*\* ([\d,\.]+)', section)
        if total_match:
            # Убираем запятые и конвертируем в число
            price_str = total_match.group(1).replace(',', '')
            apartment['total_price'] = float(price_str)
        
        # Статус
        status_match = re.search(r'\*\*Статус:\*\* (.+)', section)
        if status_match:
            apartment['status'] = status_match.group(1)
        
        # Адрес
        address_match = re.search(r'\*\*Адрес:\*\* (.+)', section)
        if address_match:
            apartment['address'] = address_match.group(1)
        
        # Название дома
        house_name_match = re.search(r'\*\*Название дома:\*\* (.+)', section)
        if house_name_match:
            apartment['house_name'] = house_name_match.group(1)
        
        return apartment if apartment else None
    
    def convert_directory(self, input_dir: str, output_file: str = None):
        """Конвертация всех MD файлов в директории в единый JSON"""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            print(f"❌ Директория не найдена: {input_dir}")
            return
        
        # Собираем все MD файлы
        md_files = sorted(input_path.glob('*.md'))
        
        if not md_files:
            print(f"❌ MD файлы не найдены в {input_dir}")
            return
        
        print(f"📁 Найдено {len(md_files)} MD файлов для конвертации\n")
        
        all_properties = []
        
        for md_file in md_files:
            print(f"📄 Обработка: {md_file.name}")
            try:
                property_data = self.parse_md_file(str(md_file))
                all_properties.append(property_data)
                print(f"  ✓ Добавлено {len(property_data.get('buildings', []))} домов")
            except Exception as e:
                print(f"  ✗ Ошибка: {e}")
        
        # Создаем общую структуру базы знаний
        knowledge_base = {
            'version': '1.0',
            'total_properties': len(all_properties),
            'properties': all_properties,
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'source': 'MM-RAG Knowledge Base',
                'format': 'structured-json'
            }
        }
        
        # Определяем путь для сохранения
        if output_file is None:
            output_file = input_path.parent / 'knowledge-base.json'
        else:
            output_file = Path(output_file)
        
        # Сохраняем JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ База знаний сохранена в: {output_file}")
        print(f"📊 Всего объектов: {len(all_properties)}")
        
        # Подсчитываем общее количество квартир
        total_apartments = sum(
            len(building.get('apartments', []))
            for prop in all_properties
            for building in prop.get('buildings', [])
        )
        print(f"🏢 Всего квартир: {total_apartments}")
        
        return str(output_file)
    
    def convert_single_file(self, md_file: str, output_file: str = None):
        """Конвертация одного MD файла в JSON"""
        if not os.path.exists(md_file):
            print(f"❌ Файл не найден: {md_file}")
            return
        
        print(f"📄 Конвертация: {md_file}")
        
        try:
            property_data = self.parse_md_file(md_file)
            
            # Определяем путь для сохранения
            if output_file is None:
                base_name = Path(md_file).stem
                output_file = Path(md_file).parent / f"{base_name}.json"
            
            # Сохраняем JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(property_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Сохранено в: {output_file}")
            return str(output_file)
            
        except Exception as e:
            print(f"❌ Ошибка при конвертации: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description='Конвертер MD файлов в JSON для MM-RAG')
    parser.add_argument(
        '--input',
        default='./quarters',
        help='Путь к директории с MD файлами или конкретному файлу'
    )
    parser.add_argument(
        '--output',
        help='Путь для сохранения JSON файла'
    )
    parser.add_argument(
        '--single',
        action='store_true',
        help='Конвертировать только один файл'
    )
    
    args = parser.parse_args()
    
    converter = MDtoJSONConverter()
    
    if args.single or args.input.endswith('.md'):
        # Конвертация одного файла
        converter.convert_single_file(args.input, args.output)
    else:
        # Конвертация директории
        converter.convert_directory(args.input, args.output)


if __name__ == "__main__":
    main()