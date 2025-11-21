#!/usr/bin/env python3
"""
Проверка документов в Knowledge Base через разные endpoints
"""

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')
agent_id = os.getenv('ELEVENLABS_AGENT_ID')
base_url = "https://api.elevenlabs.io/v1"

headers = {
    "xi-api-key": api_key
}

print("🔍 Проверка документов в Knowledge Base")
print("=" * 60)

# Пробуем разные endpoints
endpoints = [
    f"/convai/knowledge-base",
    f"/convai/agents/{agent_id}/knowledge-base",
    f"/knowledge-base",
]

for endpoint in endpoints:
    print(f"\n📌 Проверка endpoint: {endpoint}")
    url = base_url + endpoint
    
    try:
        response = requests.get(url, headers=headers)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                print(f"   ✅ Найдено элементов: {len(data)}")
                if data:
                    print(f"   Первый элемент: {str(data[0])[:100]}...")
            elif isinstance(data, dict):
                print(f"   ✅ Получен объект с ключами: {list(data.keys())}")
                if 'documents' in data:
                    print(f"      Документов: {len(data['documents'])}")
            else:
                print(f"   ⚠️ Неожиданный тип ответа: {type(data)}")
        elif response.status_code == 404:
            print(f"   ❌ Endpoint не найден")
        elif response.status_code == 401:
            print(f"   ❌ Ошибка авторизации")
        else:
            print(f"   ❌ Ошибка: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Исключение: {e}")

# Попробуем загрузить простой тестовый документ
print("\n" + "=" * 60)
print("📤 Попытка загрузить тестовый документ:")

test_content = """
Тестовый документ для проверки ElevenLabs Knowledge Base.
Квартира: Тестовая квартира №1
Цена: 100000 USD
Площадь: 50 кв.м
"""

files = {
    'file': ('test_document.txt', test_content.encode('utf-8'), 'text/plain')
}

data = {
    'name': 'Test Document MM-RAG'
}

upload_url = f"{base_url}/convai/knowledge-base"
response = requests.post(upload_url, headers=headers, files=files, data=data)

print(f"Статус загрузки: {response.status_code}")
if response.status_code in [200, 201]:
    result = response.json()
    print(f"✅ Документ загружен!")
    print(f"   ID: {result.get('id', 'Unknown')}")
    print(f"   Полный ответ: {json.dumps(result, indent=2)}")
    
    # Сохраняем ID для дальнейшего использования
    doc_id = result.get('id')
    
    if doc_id:
        print(f"\n🔗 Попытка привязать документ к агенту:")
        agent_url = f"{base_url}/convai/agents/{agent_id}"
        
        update_data = {
            "knowledge_base": [doc_id]
        }
        
        response = requests.patch(agent_url, headers={**headers, "Content-Type": "application/json"}, json=update_data)
        print(f"   Статус обновления агента: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Документ привязан к агенту")
        else:
            print(f"   ❌ Ошибка: {response.text}")
else:
    print(f"❌ Ошибка загрузки: {response.text}")

print("\n✨ Проверка завершена")