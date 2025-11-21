#!/usr/bin/env python3
import json
import os
from datetime import datetime

# Директория с квартирами
quarters_dir = "/Users/admin/MM-RAG/quarters/by-quarters"
history_file = "/Users/admin/MM-RAG/quarters_history.json"

# Загружаем текущее состояние
current_state = {}
for filename in os.listdir(quarters_dir):
    if filename.endswith('.json'):
        filepath = os.path.join(quarters_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            quarter_name = filename.replace('.json', '')
            apartments = {}
            if 'apartments' in data:
                for apt in data['apartments']:
                    apt_id = f"{apt.get('floor', '?')}-{apt.get('number', '?')}"
                    apartments[apt_id] = {
                        'status': apt.get('status', 'неизвестно'),
                        'price': apt.get('price', 'не указана'),
                        'area': apt.get('area', 'не указана')
                    }
            current_state[quarter_name] = apartments

# Загружаем предыдущее состояние если есть
try:
    with open(history_file, 'r', encoding='utf-8') as f:
        previous_state = json.load(f)
except FileNotFoundError:
    previous_state = {}
    print("Первый запуск - создаем историю")

# Сравниваем состояния
changes = {
    'sold': [],
    'new': [],
    'price_changed': [],
    'status_changed': []
}

for quarter, apartments in current_state.items():
    if quarter not in previous_state:
        # Новый квартал
        for apt_id, apt_data in apartments.items():
            changes['new'].append(f"{quarter}/{apt_id}: {apt_data['status']} - {apt_data['price']}")
    else:
        # Сравниваем квартиры
        prev_apartments = previous_state[quarter]
        
        # Проверяем новые квартиры
        for apt_id, apt_data in apartments.items():
            if apt_id not in prev_apartments:
                changes['new'].append(f"{quarter}/{apt_id}: {apt_data['status']} - {apt_data['price']}")
            else:
                # Проверяем изменения
                prev_data = prev_apartments[apt_id]
                if apt_data['status'] != prev_data['status']:
                    if apt_data['status'] == 'продана':
                        changes['sold'].append(f"{quarter}/{apt_id}: была '{prev_data['status']}' -> стала 'продана'")
                    else:
                        changes['status_changed'].append(f"{quarter}/{apt_id}: '{prev_data['status']}' -> '{apt_data['status']}'")
                
                if apt_data['price'] != prev_data['price']:
                    changes['price_changed'].append(f"{quarter}/{apt_id}: {prev_data['price']} -> {apt_data['price']}")

# Проверяем удаленные квартиры (проданные?)
for quarter, prev_apartments in previous_state.items():
    if quarter in current_state:
        current_apartments = current_state[quarter]
        for apt_id, prev_data in prev_apartments.items():
            if apt_id not in current_apartments:
                changes['sold'].append(f"{quarter}/{apt_id}: исчезла из списка (была '{prev_data['status']}')")

# Выводим изменения
print(f"\n=== ИЗМЕНЕНИЯ НА {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

if changes['sold']:
    print(f"🔴 ПРОДАННЫЕ КВАРТИРЫ ({len(changes['sold'])}):")
    for item in changes['sold']:
        print(f"  - {item}")
    print()

if changes['new']:
    print(f"🟢 НОВЫЕ КВАРТИРЫ ({len(changes['new'])}):")
    for item in changes['new'][:10]:  # Показываем первые 10
        print(f"  + {item}")
    if len(changes['new']) > 10:
        print(f"  ... и еще {len(changes['new']) - 10} квартир")
    print()

if changes['price_changed']:
    print(f"💰 ИЗМЕНЕНИЕ ЦЕН ({len(changes['price_changed'])}):")
    for item in changes['price_changed'][:5]:
        print(f"  ~ {item}")
    if len(changes['price_changed']) > 5:
        print(f"  ... и еще {len(changes['price_changed']) - 5} изменений")
    print()

if changes['status_changed']:
    print(f"📝 ИЗМЕНЕНИЕ СТАТУСА ({len(changes['status_changed'])}):")
    for item in changes['status_changed'][:5]:
        print(f"  * {item}")
    if len(changes['status_changed']) > 5:
        print(f"  ... и еще {len(changes['status_changed']) - 5} изменений")
    print()

if not any(changes.values()):
    print("Изменений не обнаружено")

# Сохраняем текущее состояние как новое предыдущее
with open(history_file, 'w', encoding='utf-8') as f:
    json.dump(current_state, f, ensure_ascii=False, indent=2)

# Статистика
total_apartments = sum(len(apts) for apts in current_state.values())
total_sold = sum(1 for quarter in current_state.values() 
                 for apt in quarter.values() if apt['status'] == 'продана')
total_available = sum(1 for quarter in current_state.values() 
                      for apt in quarter.values() if apt['status'] == 'свободна')

print("\n📊 ОБЩАЯ СТАТИСТИКА:")
print(f"  Всего квартир: {total_apartments}")
print(f"  Продано: {total_sold}")
print(f"  Свободно: {total_available}")
print(f"  Другие статусы: {total_apartments - total_sold - total_available}")