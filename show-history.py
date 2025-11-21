#!/usr/bin/env python3
"""
Скрипт для просмотра истории запусков и обновлений MM-RAG
"""

import json
from datetime import datetime
from pathlib import Path
import sys

def show_version_history():
    """Показать историю версий"""
    history_file = Path('/Users/admin/MM-RAG/quarters/version-history.json')
    
    if not history_file.exists():
        print("❌ Файл истории не найден")
        return
    
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    print("=" * 70)
    print("📊 ИСТОРИЯ ОБНОВЛЕНИЙ MM-RAG")
    print("=" * 70)
    
    if not history:
        print("История пуста")
        return
    
    # Показываем последние 10 версий
    recent_versions = history[-10:] if len(history) > 10 else history
    
    for entry in recent_versions:
        version = entry.get('version', 'N/A')
        timestamp = entry.get('timestamp', 'N/A')
        total_props = entry.get('total_properties', 0)
        total_apts = entry.get('total_apartments', 0)
        
        # Парсим время
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_time = timestamp
        
        # Изменения
        changes = entry.get('changes', {})
        summary = changes.get('summary', [])
        details = changes.get('details', {})
        
        print(f"\n📌 Версия {version}")
        print(f"   Время: {formatted_time}")
        print(f"   Объектов: {total_props}")
        print(f"   Квартир: {total_apts}")
        
        if summary:
            print(f"   Изменения:")
            for item in summary[:3]:  # Показываем первые 3 изменения
                print(f"     • {item}")
        
        # Детали изменений
        if details:
            added = len(details.get('added', []))
            removed = len(details.get('removed', []))
            price_changes = len(details.get('price_changes', []))
            status_changes = len(details.get('status_changes', []))
            
            if added > 0:
                print(f"     ➕ Добавлено: {added}")
            if removed > 0:
                print(f"     ➖ Удалено: {removed}")
            if price_changes > 0:
                print(f"     💰 Изменение цен: {price_changes}")
            if status_changes > 0:
                print(f"     📝 Изменение статусов: {status_changes}")
    
    print("\n" + "=" * 70)
    print(f"Всего версий в истории: {len(history)}")
    
    if history:
        first_date = history[0].get('timestamp', 'N/A')
        last_date = history[-1].get('timestamp', 'N/A')
        print(f"Первая запись: {first_date[:19]}")
        print(f"Последняя запись: {last_date[:19]}")
    
    print("=" * 70)

def show_monitoring_log():
    """Показать последние записи из лога мониторинга"""
    log_file = Path('/Users/admin/MM-RAG/monitoring_log.txt')
    
    if not log_file.exists():
        print("\n❌ Файл логов мониторинга не найден")
        return
    
    print("\n📝 ПОСЛЕДНИЕ ЗАПИСИ В ЛОГЕ МОНИТОРИНГА:")
    print("-" * 70)
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Показываем последние 20 строк
    recent_lines = lines[-20:] if len(lines) > 20 else lines
    
    for line in recent_lines:
        print(line.rstrip())
    
    print("-" * 70)

def show_statistics():
    """Показать статистику по кварталам"""
    quarters_dir = Path('/Users/admin/MM-RAG/quarters/by-quarters')
    
    if not quarters_dir.exists():
        print("\n❌ Директория с кварталами не найдена")
        return
    
    print("\n📊 ТЕКУЩАЯ СТАТИСТИКА ПО КВАРТАЛАМ:")
    print("-" * 70)
    
    total_apartments = 0
    quarters_data = []
    
    for json_file in sorted(quarters_dir.glob('*.json')):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        quarter_name = data.get('quarter', 'Unknown')
        count = data.get('total_apartments', 0)
        total_apartments += count
        
        if count > 0:
            quarters_data.append((quarter_name, count))
    
    # Сортируем по количеству квартир
    quarters_data.sort(key=lambda x: x[1], reverse=True)
    
    # Показываем топ-10
    for quarter, count in quarters_data[:10]:
        bar = '█' * int(count / 5)  # Масштабируем для визуализации
        print(f"{quarter:<30} | {count:>4} | {bar}")
    
    print("-" * 70)
    print(f"Всего квартир: {total_apartments}")
    print(f"Активных кварталов: {len(quarters_data)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--log":
        show_monitoring_log()
    elif len(sys.argv) > 1 and sys.argv[1] == "--stats":
        show_statistics()
    else:
        show_version_history()
        show_monitoring_log()
        show_statistics()