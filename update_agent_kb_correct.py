#!/usr/bin/env python3
"""
Правильное обновление Knowledge Base агента через conversation_config
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')
agent_id = os.getenv('ELEVENLABS_AGENT_ID')
base_url = "https://api.elevenlabs.io/v1"

headers = {
    "xi-api-key": api_key,
    "Content-Type": "application/json"
}

print("🔧 Обновление Knowledge Base агента ElevenLabs")
print("=" * 60)

# 1. Получаем текущую конфигурацию агента
agent_url = f"{base_url}/convai/agents/{agent_id}"
response = requests.get(agent_url, headers=headers)

if response.status_code != 200:
    print(f"❌ Не удалось получить данные агента: {response.status_code}")
    exit(1)

agent_data = response.json()
current_kb = agent_data.get('conversation_config', {}).get('agent', {}).get('prompt', {}).get('knowledge_base', [])

print(f"📚 Текущих документов в агенте: {len(current_kb)}")
if current_kb:
    print("   Текущие документы (первые 5):")
    for doc in current_kb[:5]:
        print(f"      - {doc.get('name')} (ID: {doc.get('id')})")

# 2. Получаем все документы из Knowledge Base
kb_url = f"{base_url}/convai/knowledge-base"
all_documents = []
next_cursor = None

print("\n📥 Получение документов из Knowledge Base...")

while True:
    params = {}
    if next_cursor:
        params['cursor'] = next_cursor
    
    response = requests.get(kb_url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        documents = data.get('documents', [])
        all_documents.extend(documents)
        
        if not data.get('has_more'):
            break
        next_cursor = data.get('next_cursor')
    else:
        print(f"❌ Ошибка получения документов: {response.status_code}")
        break

print(f"✅ Найдено {len(all_documents)} документов в Knowledge Base")

# 3. Фильтруем наши документы MM-RAG
new_kb_docs = []

for doc in all_documents:
    doc_name = doc.get('name', '')
    doc_id = doc.get('id', '')
    
    # Фильтруем наши документы (кварталы и база знаний)
    if ('MM-RAG' in doc_name or 
        'Квартал' in doc_name or 
        'Test Document' in doc_name):
        
        # Формируем объект для knowledge_base
        kb_entry = {
            "id": doc_id,
            "name": doc_name.replace(' ', '-').replace('Квартал-', ''),  # Форматируем имя
            "type": "text",
            "usage_mode": "auto"  # или "prompt" для системных документов
        }
        
        new_kb_docs.append(kb_entry)
        print(f"   ✅ Добавлен: {doc_name}")

print(f"\n📊 Подготовлено {len(new_kb_docs)} документов для обновления")

if new_kb_docs:
    # 4. Обновляем агента
    print("\n🔄 Обновление агента...")
    
    # Создаем обновление для conversation_config
    update_data = {
        "conversation_config": {
            "agent": {
                "prompt": {
                    "knowledge_base": new_kb_docs
                }
            }
        }
    }
    
    response = requests.patch(agent_url, headers=headers, json=update_data)
    
    if response.status_code == 200:
        print("✅ Агент успешно обновлен!")
        
        # Проверяем результат
        response = requests.get(agent_url, headers=headers)
        if response.status_code == 200:
            updated_data = response.json()
            updated_kb = updated_data.get('conversation_config', {}).get('agent', {}).get('prompt', {}).get('knowledge_base', [])
            
            print(f"\n📚 Документов в агенте после обновления: {len(updated_kb)}")
            if updated_kb:
                print("   Новые документы (первые 5):")
                for doc in updated_kb[:5]:
                    print(f"      - {doc.get('name')} (ID: {doc.get('id')})")
    else:
        print(f"❌ Ошибка обновления: {response.status_code}")
        print(f"   Ответ: {response.text[:500]}")
else:
    print("\n⚠️ Нет документов для добавления")

print("\n" + "=" * 60)
print("✨ Процесс завершен")