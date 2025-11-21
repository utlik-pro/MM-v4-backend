#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки обновлений в данных недвижимости bir.by
"""

import json
import requests
import os
from datetime import datetime
from typing import Dict, List, Set, Tuple

class DataUpdateChecker:
    def __init__(self, json_url: str = "https://bir.by/ai/json_ai.php"):
        self.json_url = json_url
        self.current_data = None
        self.previous_data = None
        self.snapshot_dir = "data_snapshots"
        
    def ensure_snapshot_dir(self):
        """Создает директорию для снимков если её нет"""
        if not os.path.exists(self.snapshot_dir):
            os.makedirs(self.snapshot_dir)
    
    def fetch_current_data(self) -> bool:
        """Загружает текущие данные с сайта"""
        try:
            print("📥 Загрузка текущих данных с bir.by...")
            response = requests.get(self.json_url, timeout=30)
            response.raise_for_status()
            self.current_data = response.json()
            print(f"✅ Загружено {len(self.current_data)} объектов")
            return True
        except Exception as e:
            print(f"❌ Ошибка при загрузке: {e}")
            return False
    
    def load_previous_snapshot(self) -> bool:
        """Загружает последний сохраненный снимок данных"""
        self.ensure_snapshot_dir()
        
        # Находим последний снимок
        snapshots = [f for f in os.listdir(self.snapshot_dir) if f.endswith('.json')]
        
        if not snapshots:
            print("📭 Предыдущие снимки не найдены (это первый запуск)")
            return False
        
        # Сортируем по дате в имени файла
        snapshots.sort()
        latest_snapshot = snapshots[-1]
        
        snapshot_path = os.path.join(self.snapshot_dir, latest_snapshot)
        
        try:
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                self.previous_data = json.load(f)
            print(f"📂 Загружен предыдущий снимок: {latest_snapshot}")
            print(f"   Объектов в снимке: {len(self.previous_data)}")
            return True
        except Exception as e:
            print(f"❌ Ошибка при загрузке снимка: {e}")
            return False
    
    def save_current_snapshot(self):
        """Сохраняет текущие данные как снимок"""
        if not self.current_data:
            return
        
        self.ensure_snapshot_dir()
        
        # Создаем имя файла с датой и временем
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{timestamp}.json"
        filepath = os.path.join(self.snapshot_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, ensure_ascii=False, indent=2)
            print(f"💾 Снимок сохранен: {filename}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении снимка: {e}")
    
    def compare_data(self) -> Dict:
        """Сравнивает текущие и предыдущие данные"""
        if not self.current_data:
            return {"error": "Нет текущих данных"}
        
        # Если нет предыдущих данных, все объекты новые
        if not self.previous_data:
            return {
                "added": set(self.current_data.keys()),
                "removed": set(),
                "modified": set(),
                "unchanged": set(),
                "price_changes": [],
                "status_changes": []
            }
        
        current_ids = set(self.current_data.keys())
        previous_ids = set(self.previous_data.keys())
        
        # Базовые изменения
        added = current_ids - previous_ids
        removed = previous_ids - current_ids
        common = current_ids & previous_ids
        
        # Детальный анализ изменений
        modified = set()
        unchanged = set()
        price_changes = []
        status_changes = []
        
        for item_id in common:
            current = self.current_data[item_id]
            previous = self.previous_data[item_id]
            
            has_changes = False
            
            # Проверяем изменение цены
            if current.get('Price_full') != previous.get('Price_full'):
                has_changes = True
                price_changes.append({
                    'id': item_id,
                    'apartment': current.get('Apartment', 'N/A'),
                    'old_price': previous.get('Price_full', 0),
                    'new_price': current.get('Price_full', 0),
                    'change': current.get('Price_full', 0) - previous.get('Price_full', 0)
                })
            
            # Проверяем изменение статуса
            if current.get('Status') != previous.get('Status'):
                has_changes = True
                status_changes.append({
                    'id': item_id,
                    'apartment': current.get('Apartment', 'N/A'),
                    'old_status': previous.get('Status', 'N/A'),
                    'new_status': current.get('Status', 'N/A')
                })
            
            # Проверяем другие важные поля
            important_fields = ['Square', 'Floor', 'Address', 'Quarter']
            for field in important_fields:
                if current.get(field) != previous.get(field):
                    has_changes = True
                    break
            
            if has_changes:
                modified.add(item_id)
            else:
                unchanged.add(item_id)
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": unchanged,
            "price_changes": price_changes,
            "status_changes": status_changes
        }
    
    def generate_report(self, changes: Dict) -> str:
        """Генерирует отчет об изменениях"""
        report = []
        report.append("\n" + "="*60)
        report.append("📊 ОТЧЕТ ОБ ИЗМЕНЕНИЯХ В ДАННЫХ НЕДВИЖИМОСТИ")
        report.append("="*60)
        report.append(f"Дата проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Общая статистика
        report.append("📈 ОБЩАЯ СТАТИСТИКА:")
        report.append(f"  • Всего объектов сейчас: {len(self.current_data) if self.current_data else 0}")
        report.append(f"  • Было объектов ранее: {len(self.previous_data) if self.previous_data else 0}")
        report.append("")
        
        # Изменения
        report.append("🔄 ИЗМЕНЕНИЯ:")
        report.append(f"  ✅ Добавлено новых: {len(changes['added'])}")
        report.append(f"  ❌ Удалено (продано?): {len(changes['removed'])}")
        report.append(f"  📝 Изменено: {len(changes['modified'])}")
        report.append(f"  ⏸️  Без изменений: {len(changes['unchanged'])}")
        report.append("")
        
        # Новые объекты
        if changes['added']:
            report.append("✅ НОВЫЕ ОБЪЕКТЫ:")
            for i, item_id in enumerate(list(changes['added'])[:10], 1):
                item = self.current_data[item_id]
                report.append(f"  {i}. {item.get('Apartment', 'N/A')}")
                report.append(f"     Квартал: {item.get('Quarter', 'N/A')}")
                report.append(f"     Площадь: {item.get('Square', 'N/A')}")
                report.append(f"     Цена: {item.get('Price_full', 'N/A')} EUR")
            if len(changes['added']) > 10:
                report.append(f"  ... и еще {len(changes['added']) - 10} объектов")
            report.append("")
        
        # Удаленные объекты
        if changes['removed']:
            report.append("❌ УДАЛЕННЫЕ ОБЪЕКТЫ (возможно проданы):")
            for i, item_id in enumerate(list(changes['removed'])[:10], 1):
                if self.previous_data and item_id in self.previous_data:
                    item = self.previous_data[item_id]
                    report.append(f"  {i}. {item.get('Apartment', 'N/A')}")
                    report.append(f"     Квартал: {item.get('Quarter', 'N/A')}")
                    report.append(f"     Площадь: {item.get('Square', 'N/A')}")
                    report.append(f"     Была цена: {item.get('Price_full', 'N/A')} EUR")
            if len(changes['removed']) > 10:
                report.append(f"  ... и еще {len(changes['removed']) - 10} объектов")
            report.append("")
        
        # Изменения цен
        if changes['price_changes']:
            report.append("💰 ИЗМЕНЕНИЯ ЦЕН:")
            # Сортируем по изменению цены
            sorted_prices = sorted(changes['price_changes'], key=lambda x: abs(x['change']), reverse=True)
            for i, change in enumerate(sorted_prices[:10], 1):
                emoji = "📈" if change['change'] > 0 else "📉"
                report.append(f"  {i}. {emoji} {change['apartment']}")
                report.append(f"     Было: {change['old_price']} EUR → Стало: {change['new_price']} EUR")
                report.append(f"     Изменение: {change['change']:+.0f} EUR ({change['change']/change['old_price']*100:+.1f}%)" if change['old_price'] > 0 else "")
            if len(changes['price_changes']) > 10:
                report.append(f"  ... и еще {len(changes['price_changes']) - 10} изменений цен")
            report.append("")
        
        # Изменения статусов
        if changes['status_changes']:
            report.append("📋 ИЗМЕНЕНИЯ СТАТУСОВ:")
            for i, change in enumerate(changes['status_changes'][:10], 1):
                report.append(f"  {i}. {change['apartment']}")
                report.append(f"     Было: {change['old_status']} → Стало: {change['new_status']}")
            if len(changes['status_changes']) > 10:
                report.append(f"  ... и еще {len(changes['status_changes']) - 10} изменений статусов")
            report.append("")
        
        report.append("="*60)
        
        return "\n".join(report)
    
    def save_report(self, report: str):
        """Сохраняет отчет в файл"""
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"update_report_{timestamp}.txt"
        filepath = os.path.join(reports_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Отчет сохранен: {filepath}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении отчета: {e}")

def main():
    """Основная функция"""
    print("🔍 Проверка обновлений данных недвижимости BIR.BY")
    print("="*50)
    
    checker = DataUpdateChecker()
    
    # Загружаем текущие данные
    if not checker.fetch_current_data():
        print("Не удалось загрузить данные")
        return
    
    # Загружаем предыдущий снимок
    has_previous = checker.load_previous_snapshot()
    
    # Сравниваем данные
    if has_previous:
        print("\n🔍 Сравнение данных...")
        changes = checker.compare_data()
        
        # Генерируем и выводим отчет
        report = checker.generate_report(changes)
        print(report)
        
        # Сохраняем отчет
        checker.save_report(report)
    else:
        print("\n📝 Это первый запуск - сохраняем базовый снимок данных")
    
    # Сохраняем текущий снимок
    checker.save_current_snapshot()
    
    print("\n✅ Проверка завершена!")

if __name__ == "__main__":
    main()