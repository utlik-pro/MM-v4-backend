#!/usr/bin/env python3
"""
Проверка статуса документов и добавление готовых к агенту
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

print("🔍 Проверка и добавление документов в агента")
print("=" * 60)

# 1. Получаем все документы из KB
kb_url = f"{base_url}/convai/knowledge-base"
response = requests.get(kb_url, headers=headers)

if response.status_code != 200:
    print(f"❌ Ошибка получения документов: {response.status_code}")
    exit(1)

data = response.json()
documents = data.get('documents', [])

print(f"📚 Найдено {len(documents)} документов в Knowledge Base")

# 2. Фильтруем наши документы и проверяем RAG индекс
ready_docs = []

for doc in documents[:20]:  # Проверим первые 20
    doc_name = doc.get('name', '')
    doc_id = doc.get('id', '')
    
    if ('MM-RAG' in doc_name or 'Квартал' in doc_name):
        # Проверяем RAG индекс
        rag_url = f"{base_url}/convai/knowledge-base/{doc_id}/rag-index"
        rag_response = requests.get(rag_url, headers=headers)
        
        if rag_response.status_code == 200:
            rag_data = rag_response.json()
            
            if 'indexes' in rag_data and rag_data['indexes']:
                index_status = rag_data['indexes'][0].get('status')
                if index_status == 'succeeded':
                    ready_docs.append({
                        'id': doc_id,
                        'name': doc_name,
                        'status': index_status
                    })
                    print(f"   ✅ {doc_name}: RAG готов")
                else:
                    print(f"   ⏳ {doc_name}: RAG статус {index_status}")
            else:
                print(f"   ❌ {doc_name}: нет RAG индекса")

print(f"\n📊 Готово к добавлению: {len(ready_docs)} документов")

if ready_docs:
    # 3. Получаем текущую конфигурацию агента
    agent_url = f"{base_url}/convai/agents/{agent_id}"
    response = requests.get(agent_url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Не удалось получить данные агента")
        exit(1)
    
    agent_data = response.json()
    current_kb = agent_data.get('conversation_config', {}).get('agent', {}).get('prompt', {}).get('knowledge_base', [])
    
    print(f"\n🤖 Текущих документов в агенте: {len(current_kb)}")
    
    # Проверяем, какие документы уже есть
    existing_ids = {doc['id'] for doc in current_kb}
    
    # Добавляем только новые
    new_docs = []
    for doc in ready_docs[:5]:  # Добавим первые 5 новых
        if doc['id'] not in existing_ids:
            kb_entry = {
                "id": doc['id'],
                "name": doc['name'].replace(' ', '-').replace('Квартал-', ''),
                "type": "text",
                "usage_mode": "auto"
            }
            current_kb.append(kb_entry)
            new_docs.append(doc['name'])
    
    if new_docs:
        print(f"\n📝 Добавляем {len(new_docs)} новых документов:")
        for name in new_docs:
            print(f"   - {name}")
        
        # 4. Обновляем агента
        update_data = {
            "conversation_config": {
                "agent": {
                    "prompt": {
                        "knowledge_base": current_kb
                    }
                }
            }
        }
        
        response = requests.patch(agent_url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            print(f"\n✅ Агент обновлен! Всего документов: {len(current_kb)}")
        else:
            print(f"\n❌ Ошибка обновления: {response.status_code}")
            error = response.json()
            print(f"   Детали: {error}")
    else:
        print("\n✅ Все документы уже добавлены в агента")

print("\n" + "=" * 60)
print("✨ Процесс завершен")