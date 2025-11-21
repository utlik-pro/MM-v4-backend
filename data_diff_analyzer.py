#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import hashlib
from datetime import datetime
import os
from typing import Dict, List, Any, Tuple
import difflib

class DataDiffAnalyzer:
    def __init__(self):
        self.url = "https://bir.by/ai/json_ai.php"
        self.cache_dir = "cache"
        self.current_data = None
        self.previous_data = None
        
    def decode_unicode(self, text: str) -> str:
        """Декодирует Unicode последовательности в тексте"""
        if not text:
            return ""
        
        try:
            # Заменяем \u последовательности на соответствующие символы
            decoded = text.encode().decode('unicode_escape')
            return decoded
        except Exception as e:
            print(f"Ошибка декодирования Unicode: {e}")
            return text
    
    def load_current_data(self) -> bool:
        """Загружает текущие данные с сервера"""
        try:
            print("📥 Загрузка текущих данных...")
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()
            
            self.current_data = response.json()
            print(f"✅ Загружено {len(self.current_data)} объектов")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {e}")
            return False
    
    def load_previous_data(self) -> bool:
        """Загружает предыдущие данные из кэша"""
        try:
            cache_file = os.path.join(self.cache_dir, "previous_data.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.previous_data = json.load(f)
                print(f"✅ Загружены предыдущие данные: {len(self.previous_data)} объектов")
                return True
            else:
                print("⚠️ Файл предыдущих данных не найден")
                return False
        except Exception as e:
            print(f"❌ Ошибка загрузки предыдущих данных: {e}")
            return False
    
    def save_current_as_previous(self):
        """Сохраняет текущие данные как предыдущие для следующего сравнения"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            cache_file = os.path.join(self.cache_dir, "previous_data.json")
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Текущие данные сохранены для следующего сравнения")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения данных: {e}")
    
    def compare_objects(self, obj1: Dict, obj2: Dict) -> Dict[str, Any]:
        """Сравнивает два объекта и возвращает различия"""
        changes = {}
        
        # Ключи для сравнения
        keys_to_compare = ['Price', 'Status', 'Area', 'Floor', 'Rooms', 'NameHouse', 'Address', 'Quarter']
        
        for key in keys_to_compare:
            val1 = self.decode_unicode(str(obj1.get(key, '')))
            val2 = self.decode_unicode(str(obj2.get(key, '')))
            
            if val1 != val2:
                changes[key] = {
                    'old': val2,
                    'new': val1
                }
        
        return changes
    
    def analyze_differences(self) -> Dict[str, Any]:
        """Анализирует различия между текущими и предыдущими данными"""
        if not self.current_data or not self.previous_data:
            return {}
        
        results = {
            'new_objects': [],
            'removed_objects': [],
            'changed_objects': [],
            'statistics': {
                'total_current': len(self.current_data),
                'total_previous': len(self.previous_data),
                'new_count': 0,
                'removed_count': 0,
                'changed_count': 0
            }
        }
        
        current_ids = set(self.current_data.keys())
        previous_ids = set(self.previous_data.keys())
        
        # Новые объекты
        new_ids = current_ids - previous_ids
        for obj_id in new_ids:
            obj = self.current_data[obj_id]
            results['new_objects'].append({
                'id': obj_id,
                'house': self.decode_unicode(obj.get('NameHouse', '')),
                'address': self.decode_unicode(obj.get('Address', '')),
                'price': self.decode_unicode(obj.get('Price', '')),
                'rooms': self.decode_unicode(obj.get('Rooms', '')),
                'area': self.decode_unicode(obj.get('Area', ''))
            })
        
        # Удаленные объекты
        removed_ids = previous_ids - current_ids
        for obj_id in removed_ids:
            obj = self.previous_data[obj_id]
            results['removed_objects'].append({
                'id': obj_id,
                'house': self.decode_unicode(obj.get('NameHouse', '')),
                'address': self.decode_unicode(obj.get('Address', '')),
                'price': self.decode_unicode(obj.get('Price', '')),
                'rooms': self.decode_unicode(obj.get('Rooms', '')),
                'area': self.decode_unicode(obj.get('Area', ''))
            })
        
        # Измененные объекты
        common_ids = current_ids & previous_ids
        for obj_id in common_ids:
            changes = self.compare_objects(
                self.current_data[obj_id], 
                self.previous_data[obj_id]
            )
            
            if changes:
                obj = self.current_data[obj_id]
                results['changed_objects'].append({
                    'id': obj_id,
                    'house': self.decode_unicode(obj.get('NameHouse', '')),
                    'address': self.decode_unicode(obj.get('Address', '')),
                    'changes': changes
                })
        
        # Обновляем статистику
        results['statistics']['new_count'] = len(new_ids)
        results['statistics']['removed_count'] = len(removed_ids)
        results['statistics']['changed_count'] = len(results['changed_objects'])
        
        return results
    
    def print_differences(self, differences: Dict[str, Any]):
        """Выводит различия в удобочитаемом формате"""
        stats = differences.get('statistics', {})
        
        print("\n" + "="*60)
        print("📊 АНАЛИЗ ИЗМЕНЕНИЙ В ДАННЫХ BIR.BY")
        print("="*60)
        
        print(f"\n📈 Общая статистика:")
        print(f"  • Текущих объектов: {stats.get('total_current', 0)}")
        print(f"  • Предыдущих объектов: {stats.get('total_previous', 0)}")
        print(f"  • Новых объектов: {stats.get('new_count', 0)}")
        print(f"  • Удаленных объектов: {stats.get('removed_count', 0)}")
        print(f"  • Измененных объектов: {stats.get('changed_count', 0)}")
        
        # Новые объекты
        if differences.get('new_objects'):
            print(f"\n🆕 НОВЫЕ ОБЪЕКТЫ ({len(differences['new_objects'])}):")
            for i, obj in enumerate(differences['new_objects'][:10], 1):
                print(f"  {i}. ID: {obj['id']}")
                print(f"     🏠 {obj['house']}")
                print(f"     📍 {obj['address']}")
                print(f"     💰 {obj['price']} | 🏠 {obj['rooms']} комн. | 📐 {obj['area']} м²")
                print()
            
            if len(differences['new_objects']) > 10:
                print(f"     ... и еще {len(differences['new_objects']) - 10} объектов")
        
        # Удаленные объекты
        if differences.get('removed_objects'):
            print(f"\n🗑️ УДАЛЕННЫЕ ОБЪЕКТЫ ({len(differences['removed_objects'])}):")
            for i, obj in enumerate(differences['removed_objects'][:10], 1):
                print(f"  {i}. ID: {obj['id']}")
                print(f"     🏠 {obj['house']}")
                print(f"     📍 {obj['address']}")
                print(f"     💰 {obj['price']} | 🏠 {obj['rooms']} комн. | 📐 {obj['area']} м²")
                print()
            
            if len(differences['removed_objects']) > 10:
                print(f"     ... и еще {len(differences['removed_objects']) - 10} объектов")
        
        # Измененные объекты
        if differences.get('changed_objects'):
            print(f"\n🔄 ИЗМЕНЕННЫЕ ОБЪЕКТЫ ({len(differences['changed_objects'])}):")
            for i, obj in enumerate(differences['changed_objects'][:15], 1):
                print(f"  {i}. ID: {obj['id']}")
                print(f"     🏠 {obj['house']}")
                print(f"     📍 {obj['address']}")
                
                for field, change in obj['changes'].items():
                    field_names = {
                        'Price': '💰 Цена',
                        'Status': '📊 Статус',
                        'Area': '📐 Площадь',
                        'Floor': '🏢 Этаж',
                        'Rooms': '🏠 Комнаты',
                        'NameHouse': '🏠 Название дома',
                        'Address': '📍 Адрес',
                        'Quarter': '🏘️ Квартал'
                    }
                    
                    field_name = field_names.get(field, field)
                    print(f"     {field_name}: '{change['old']}' → '{change['new']}'")
                
                print()
            
            if len(differences['changed_objects']) > 15:
                print(f"     ... и еще {len(differences['changed_objects']) - 15} объектов")
        
        if not any([differences.get('new_objects'), differences.get('removed_objects'), differences.get('changed_objects')]):
            print("\n✅ Изменений не обнаружено")
    
    def save_diff_report(self, differences: Dict[str, Any]):
        """Сохраняет отчет об изменениях в файл"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"diff_report_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(differences, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Отчет сохранен в файл: {filename}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения отчета: {e}")

def main():
    analyzer = DataDiffAnalyzer()
    
    print("🔍 Анализатор изменений данных BIR.BY")
    print("="*50)
    
    # Загружаем текущие данные
    if not analyzer.load_current_data():
        return
    
    # Загружаем предыдущие данные
    if not analyzer.load_previous_data():
        print("⚠️ Предыдущие данные не найдены. Сохраняем текущие для следующего сравнения...")
        analyzer.save_current_as_previous()
        return
    
    # Анализируем различия
    differences = analyzer.analyze_differences()
    
    # Выводим результаты
    analyzer.print_differences(differences)
    
    # Сохраняем отчет
    analyzer.save_diff_report(differences)
    
    # Сохраняем текущие данные для следующего сравнения
    analyzer.save_current_as_previous()

if __name__ == "__main__":
    main()
