#!/usr/bin/env python3
"""
Тестовый скрипт для проверки ElevenLabs API и привязки документов
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

print("🔍 Проверка ElevenLabs API")
print("=" * 60)

# 1. Получаем информацию об агенте
print("\n1️⃣ Информация об агенте:")
agent_url = f"{base_url}/convai/agents/{agent_id}"
response = requests.get(agent_url, headers=headers)

if response.status_code == 200:
    agent_data = response.json()
    print(f"✅ Агент: {agent_data.get('name', 'Unknown')}")
    print(f"   ID: {agent_id}")
    
    current_kb = agent_data.get('knowledge_base', [])
    print(f"   Текущих документов: {len(current_kb)}")
    
    if current_kb:
        print("   Текущие документы в агенте:")
        for doc_id in current_kb[:5]:  # Показываем первые 5
            print(f"      - {doc_id}")
else:
    print(f"❌ Ошибка {response.status_code}: {response.text}")
    exit(1)

# 2. Получаем список всех документов в Knowledge Base
print("\n2️⃣ Все документы в Knowledge Base:")
kb_url = f"{base_url}/convai/knowledge-base"
response = requests.get(kb_url, headers=headers)

all_doc_ids = []
if response.status_code == 200:
    kb_data = response.json()
    
    # Обрабатываем разные форматы ответа
    if isinstance(kb_data, list):
        print(f"✅ Найдено документов: {len(kb_data)}")
        
        # Показываем первые 10
        for i, doc in enumerate(kb_data[:10]):
            if isinstance(doc, str):
                print(f"   {i+1}. ID: {doc}")
                all_doc_ids.append(doc)
            elif isinstance(doc, dict):
                print(f"   {i+1}. {doc.get('name', 'Unknown')} (ID: {doc.get('id', 'Unknown')})")
                all_doc_ids.append(doc.get('id'))
        
        if len(kb_data) > 10:
            print(f"   ... и еще {len(kb_data) - 10} документов")
            # Собираем все ID
            for doc in kb_data[10:]:
                if isinstance(doc, str):
                    all_doc_ids.append(doc)
                elif isinstance(doc, dict):
                    all_doc_ids.append(doc.get('id'))
else:
    print(f"❌ Ошибка {response.status_code}: {response.text}")
    exit(1)

# 3. Пытаемся обновить агента с ПЕРВЫМИ 5 документами
print("\n3️⃣ Попытка обновить агента с первыми 5 документами:")
test_doc_ids = all_doc_ids[:5]

print(f"   Добавляем документы:")
for doc_id in test_doc_ids:
    print(f"      - {doc_id}")

update_data = {
    "knowledge_base": test_doc_ids
}

print("\n   Отправка запроса...")
response = requests.patch(agent_url, headers=headers, json=update_data)

if response.status_code == 200:
    print("✅ Запрос успешно отправлен")
    
    # Ждем синхронизацию
    print("⏳ Ожидание 3 секунды...")
    time.sleep(3)
    
    # Проверяем результат
    print("\n4️⃣ Проверка результата:")
    response = requests.get(agent_url, headers=headers)
    if response.status_code == 200:
        updated_agent = response.json()
        new_kb = updated_agent.get('knowledge_base', [])
        print(f"✅ Документов в агенте после обновления: {len(new_kb)}")
        
        if new_kb:
            print("   Документы в агенте:")
            for doc_id in new_kb[:10]:
                print(f"      - {doc_id}")
else:
    print(f"❌ Ошибка обновления: {response.status_code}")
    print(f"   Ответ: {response.text}")

print("\n" + "=" * 60)
print("✨ Тест завершен")