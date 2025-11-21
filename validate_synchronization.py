#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексная проверка синхронизации данных BIR.BY
"""

import json
import requests
import re
import os
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class DataValidator:
    def __init__(self):
        self.api_data = {}
        self.markdown_data = defaultdict(list)
        self.errors = []
        self.warnings = []
        self.stats = {}
        
    def decode_unicode(self, text):
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
    
    def load_api_data(self):
        """Загружает данные из API"""
        print("📥 Загрузка данных из API...")
        url = "https://bir.by/ai/json_ai.php"
        response = requests.get(url, timeout=30)
        self.api_data = response.json()
        print(f"✅ Загружено {len(self.api_data)} объектов из API")
        
    def extract_quarter_number(self, quarter_str):
        """Извлекает номер квартала из строки"""
        if not quarter_str:
            return None
        # Декодируем Unicode
        decoded = self.decode_unicode(quarter_str)
        # Ищем число в начале строки
        match = re.match(r'^(\d+)', decoded)
        if match:
            return int(match.group(1))
        return None
    
    def determine_quarter_by_house(self, house_number):
        """Определяет квартал по номеру дома"""
        if not house_number:
            return None
        decoded = self.decode_unicode(house_number)
        
        # Особые случаи - Волна 7с и 8с всегда во 2 квартале
        if 'Волна 7с' in decoded or 'Волна 8с' in decoded:
            return 2
            
        # Извлекаем числовую часть номера дома (до точки)
        match = re.search(r'(\d+)\.', decoded)
        if match:
            return int(match.group(1))
        
        # Если есть просто число
        match = re.search(r'(\d+)', decoded)
        if match:
            num = int(match.group(1))
            # Дома с номерами меньше 50 обычно имеют явный квартал
            if num < 50:
                return num
        
        return None
    
    def load_markdown_files(self):
        """Загружает данные из markdown файлов"""
        print("\n📂 Загрузка markdown файлов...")
        quarters_dir = "quarters"
        
        if not os.path.exists(quarters_dir):
            self.errors.append("❌ Директория quarters не найдена")
            return
            
        for filename in os.listdir(quarters_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(quarters_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Извлекаем номер квартала из имени файла
                quarter_match = re.match(r'^(\d+)', filename)
                if quarter_match:
                    quarter_num = int(quarter_match.group(1))
                else:
                    continue
                    
                # Парсим апартаменты из файла
                apartments = re.findall(r'### 🏠 (?:Квартира|Пентхаус|Бизнес-апартаменты) №[№]?(\d+)', content)
                for apt_num in apartments:
                    self.markdown_data[quarter_num].append(apt_num)
                    
        print(f"✅ Загружено {len(self.markdown_data)} кварталов из markdown")
        
    def validate_no_parking(self):
        """Проверяет отсутствие машиномест в данных"""
        print("\n🚗 Проверка отсутствия машиномест...")
        parking_count = 0
        
        for item_id, item in self.api_data.items():
            obj_type = self.decode_unicode(item.get('type', '')).lower()
            apartment = self.decode_unicode(item.get('Apartment', '')).lower()
            
            if 'машиноместо' in obj_type or 'машиноместо' in apartment:
                parking_count += 1
                
        if parking_count > 0:
            self.warnings.append(f"⚠️ Найдено {parking_count} машиномест в API (должны быть исключены)")
        else:
            print("✅ Машиноместа успешно исключены")
            
    def validate_duplicates(self):
        """Проверяет наличие дубликатов"""
        print("\n🔍 Проверка дубликатов...")
        
        # Проверка дубликатов в markdown файлах
        all_apartments = []
        for quarter, apts in self.markdown_data.items():
            for apt in apts:
                all_apartments.append((quarter, apt))
                
        # Ищем дубликаты
        seen = set()
        duplicates = []
        for quarter, apt in all_apartments:
            if apt in seen:
                duplicates.append(f"Квартира №{apt} (квартал {quarter})")
            seen.add(apt)
            
        if duplicates:
            self.errors.append(f"❌ Найдены дубликаты: {', '.join(duplicates[:5])}")
        else:
            print("✅ Дубликатов не найдено")
            
    def validate_quarter_assignment(self):
        """Проверяет правильность распределения по кварталам"""
        print("\n🏘️ Проверка правил распределения по кварталам...")
        
        incorrect_assignments = []
        
        for item_id, item in self.api_data.items():
            # Пропускаем машиноместа
            obj_type = self.decode_unicode(item.get('type', '')).lower()
            if 'машиноместо' in obj_type:
                continue
                
            quarter_str = self.decode_unicode(item.get('Quarter', ''))
            house_number = self.decode_unicode(item.get('NumberHouse', ''))
            apartment = self.decode_unicode(item.get('Apartment', ''))
            
            # Определяем ожидаемый квартал
            expected_quarter = self.extract_quarter_number(quarter_str)
            
            # Для объектов без квартала пробуем определить по номеру дома
            if not expected_quarter and house_number:
                expected_quarter = self.determine_quarter_by_house(house_number)
                
            if expected_quarter:
                # Проверяем, есть ли объект в правильном квартале
                apt_num_match = re.search(r'№(\d+)', apartment)
                if apt_num_match:
                    apt_num = apt_num_match.group(1)
                    
                    # Проверяем наличие в markdown
                    found_in_quarter = None
                    for q, apts in self.markdown_data.items():
                        if apt_num in apts:
                            found_in_quarter = q
                            break
                            
                    if found_in_quarter and found_in_quarter != expected_quarter:
                        # Особый случай для Волна 7с и 8с
                        if 'Волна' not in house_number or expected_quarter != 2:
                            incorrect_assignments.append(
                                f"{apartment} должен быть в квартале {expected_quarter}, но находится в {found_in_quarter}"
                            )
                            
        if incorrect_assignments:
            self.errors.append(f"❌ Неправильное распределение: {'; '.join(incorrect_assignments[:3])}")
        else:
            print("✅ Все объекты в правильных кварталах")
            
    def validate_completeness(self):
        """Проверяет полноту данных"""
        print("\n📊 Проверка полноты данных...")
        
        # Собираем все апартаменты из API (без машиномест)
        api_apartments = set()
        for item_id, item in self.api_data.items():
            obj_type = self.decode_unicode(item.get('type', '')).lower()
            if 'машиноместо' in obj_type:
                continue
                
            apartment = self.decode_unicode(item.get('Apartment', ''))
            apt_num_match = re.search(r'№(\d+)', apartment)
            if apt_num_match:
                api_apartments.add(apt_num_match.group(1))
                
        # Собираем все апартаменты из markdown
        markdown_apartments = set()
        for apts in self.markdown_data.values():
            markdown_apartments.update(apts)
            
        # Находим пропущенные
        missing_in_markdown = api_apartments - markdown_apartments
        extra_in_markdown = markdown_apartments - api_apartments
        
        if missing_in_markdown:
            self.errors.append(f"❌ Отсутствуют в markdown: №{', №'.join(sorted(missing_in_markdown)[:10])}")
        
        if extra_in_markdown:
            self.warnings.append(f"⚠️ Лишние в markdown: №{', №'.join(sorted(extra_in_markdown)[:10])}")
            
        print(f"📈 Объектов в API: {len(api_apartments)}")
        print(f"📄 Объектов в markdown: {len(markdown_apartments)}")
        
        if len(api_apartments) == len(markdown_apartments):
            print("✅ Количество объектов совпадает")
        
        self.stats = {
            'api_total': len(self.api_data),
            'api_residential': len(api_apartments),
            'markdown_total': len(markdown_apartments),
            'quarters_count': len(self.markdown_data),
            'missing_count': len(missing_in_markdown),
            'extra_count': len(extra_in_markdown)
        }
        
    def check_special_cases(self):
        """Проверяет особые случаи"""
        print("\n🔎 Проверка особых случаев...")
        
        # Проверка Диадемы (должна быть во 2 квартале)
        diadema_count = 0
        diadema_in_q2 = 0
        
        for item_id, item in self.api_data.items():
            house_name = self.decode_unicode(item.get('NameHouse', '')).lower()
            if 'диадема' in house_name or 'diadema' in house_name:
                diadema_count += 1
                
                apartment = self.decode_unicode(item.get('Apartment', ''))
                apt_num_match = re.search(r'№(\d+)', apartment)
                if apt_num_match:
                    apt_num = apt_num_match.group(1)
                    if apt_num in self.markdown_data.get(2, []):
                        diadema_in_q2 += 1
                        
        print(f"📍 Диадема: {diadema_in_q2}/{diadema_count} объектов во 2 квартале")
        
        # Проверка домов 18.x (должны быть в 18 квартале)
        house_18_correct = 0
        house_18_total = 0
        
        for item_id, item in self.api_data.items():
            house_number = self.decode_unicode(item.get('NumberHouse', ''))
            if re.match(r'^18\.\d', house_number):
                house_18_total += 1
                
                apartment = self.decode_unicode(item.get('Apartment', ''))
                apt_num_match = re.search(r'№(\d+)', apartment)
                if apt_num_match:
                    apt_num = apt_num_match.group(1)
                    if apt_num in self.markdown_data.get(18, []):
                        house_18_correct += 1
                        
        if house_18_total > 0:
            print(f"📍 Дома 18.x: {house_18_correct}/{house_18_total} объектов в 18 квартале")
            
    def generate_report(self):
        """Генерирует отчет о валидации"""
        print("\n" + "="*60)
        print("📋 ОТЧЕТ О ВАЛИДАЦИИ ДАННЫХ")
        print("="*60)
        
        # Статистика
        print("\n📊 Статистика:")
        for key, value in self.stats.items():
            print(f"  • {key}: {value}")
            
        # Ошибки
        if self.errors:
            print(f"\n❌ Найдено ошибок: {len(self.errors)}")
            for error in self.errors:
                print(f"  {error}")
        else:
            print("\n✅ Критических ошибок не найдено")
            
        # Предупреждения
        if self.warnings:
            print(f"\n⚠️ Предупреждений: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  {warning}")
                
        # Сохраняем отчет
        report = {
            'stats': self.stats,
            'errors': self.errors,
            'warnings': self.warnings,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        with open('validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        print("\n📄 Отчет сохранен в validation_report.json")
        
        # Итоговый статус
        if not self.errors:
            print("\n✅ СИНХРОНИЗАЦИЯ УСПЕШНА!")
        else:
            print(f"\n⚠️ ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ {len(self.errors)} ОШИБОК")
            
    def run(self):
        """Запускает полную валидацию"""
        print("🚀 Запуск валидации данных BIR.BY\n")
        
        self.load_api_data()
        self.load_markdown_files()
        
        self.validate_no_parking()
        self.validate_duplicates()
        self.validate_quarter_assignment()
        self.validate_completeness()
        self.check_special_cases()
        
        self.generate_report()

if __name__ == "__main__":
    validator = DataValidator()
    validator.run()