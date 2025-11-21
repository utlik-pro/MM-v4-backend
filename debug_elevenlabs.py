#!/usr/bin/env python3
"""
Детальная диагностика ElevenLabs API для понимания проблемы с привязкой документов
"""

import os
import json
import requests
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')
agent_id = os.getenv('ELEVENLABS_AGENT_ID')
base_url = "https://api.elevenlabs.io/v1"

headers = {
    "xi-api-key": api_key,
    "Content-Type": "application/json"
}

print("🔍 Детальная диагностика ElevenLabs API")
print("=" * 60)

# 1. Проверяем права API ключа
print("\n1️⃣ Проверка прав API ключа...")
test_endpoints = [
    ("/convai/agents", "GET", "Чтение списка агентов"),
    (f"/convai/agents/{agent_id}", "GET", "Чтение информации об агенте"),
    (f"/convai/agents/{agent_id}", "PATCH", "Обновление агента"),
    ("/convai/knowledge-base", "GET", "Чтение Knowledge Base"),
    ("/convai/knowledge-base", "POST", "Добавление в Knowledge Base"),
]

for endpoint, method, description in test_endpoints:
    url = base_url + endpoint
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "PATCH":
        # Пустой PATCH для проверки прав
        response = requests.patch(url, headers=headers, json={})
    elif method == "POST":
        # Не отправляем реальный POST
        print(f"   {method} {endpoint}: {description} - пропущено (не тестируем POST)")
        continue
    
    if response.status_code in [200, 201, 204]:
        print(f"   ✅ {method} {endpoint}: {description} - доступно")
    elif response.status_code == 401:
        print(f"   ❌ {method} {endpoint}: {description} - нет прав")
    elif response.status_code == 404:
        print(f"   ⚠️ {method} {endpoint}: {description} - endpoint не найден")
    else:
        print(f"   ⚠️ {method} {endpoint}: {description} - код {response.status_code}")

# 2. Получаем детальную информацию об агенте
print("\n2️⃣ Детальная информация об агенте...")
agent_url = f"{base_url}/convai/agents/{agent_id}"
response = requests.get(agent_url, headers=headers)

if response.status_code == 200:
    agent_data = response.json()
    
    # Сохраняем для анализа
    with open('agent_full_data.json', 'w', encoding='utf-8') as f:
        json.dump(agent_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Данные агента сохранены в agent_full_data.json")
    
    # Анализируем структуру
    print("\n   Структура данных агента:")
    for key in agent_data.keys():
        value = agent_data[key]
        if isinstance(value, list):
            print(f"      - {key}: массив из {len(value)} элементов")
        elif isinstance(value, dict):
            print(f"      - {key}: объект с {len(value)} ключами")
        else:
            print(f"      - {key}: {type(value).__name__}")
    
    # Проверяем knowledge_base
    kb = agent_data.get('knowledge_base', [])
    print(f"\n   Knowledge Base статус:")
    print(f"      - Тип данных: {type(kb)}")
    print(f"      - Количество элементов: {len(kb)}")
    if kb:
        print(f"      - Первый элемент: {kb[0]}")

# 3. Пробуем разные форматы обновления
print("\n3️⃣ Тестирование разных форматов обновления knowledge_base...")

test_formats = [
    {
        "name": "Массив строк (ID документов)",
        "data": {"knowledge_base": ["TwkSu4qxmhNw8fkpnfch"]}
    },
    {
        "name": "Массив объектов",
        "data": {"knowledge_base": [{"id": "TwkSu4qxmhNw8fkpnfch"}]}
    },
    {
        "name": "Строка с одним ID",
        "data": {"knowledge_base": "TwkSu4qxmhNw8fkpnfch"}
    },
    {
        "name": "Объект с documents",
        "data": {"knowledge_base": {"documents": ["TwkSu4qxmhNw8fkpnfch"]}}
    }
]

for test in test_formats:
    print(f"\n   Тест: {test['name']}")
    print(f"   Отправляем: {json.dumps(test['data'])}")
    
    response = requests.patch(agent_url, headers=headers, json=test['data'])
    
    if response.status_code == 200:
        result = response.json()
        new_kb = result.get('knowledge_base', [])
        print(f"   ✅ Успех! KB содержит: {len(new_kb)} элементов")
        
        if new_kb:
            print(f"   🎉 ФОРМАТ РАБОТАЕТ! Используйте этот формат")
            break
    else:
        print(f"   ❌ Ошибка {response.status_code}")
        if response.status_code == 400:
            print(f"      Детали: {response.text[:200]}")
    
    time.sleep(1)  # Пауза между тестами

# 4. Проверяем альтернативные endpoints
print("\n4️⃣ Проверка альтернативных endpoints...")

alt_endpoints = [
    f"/convai/agents/{agent_id}/knowledge-base",
    f"/convai/agents/{agent_id}/documents",
    f"/agents/{agent_id}/knowledge-base",
]

for endpoint in alt_endpoints:
    url = base_url + endpoint
    print(f"\n   Проверка: {endpoint}")
    
    # GET запрос
    response = requests.get(url, headers=headers)
    print(f"      GET: {response.status_code}")
    
    # PATCH запрос
    response = requests.patch(url, headers=headers, json={"documents": ["test"]})
    print(f"      PATCH: {response.status_code}")

print("\n" + "=" * 60)
print("✨ Диагностика завершена")
print("\nРекомендации:")
print("1. Проверьте файл agent_full_data.json для анализа структуры")
print("2. Если ни один формат не работает, возможно требуется:")
print("   - Использовать веб-интерфейс")
print("   - Обновить права API ключа")
print("   - Обратиться в поддержку ElevenLabs")