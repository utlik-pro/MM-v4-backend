#!/usr/bin/env python3
"""
Привязка всех документов из Knowledge Base к агенту
"""

import os
import requests
from dotenv import load_dotenv
import json
import time

load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')
agent_id = os.getenv('ELEVENLABS_AGENT_ID')
base_url = "https://api.elevenlabs.io/v1"

headers = {
    "xi-api-key": api_key,
    "Content-Type": "application/json"
}

print("🔗 Привязка документов к агенту ElevenLabs")
print("=" * 60)

# 1. Получаем все документы из Knowledge Base
kb_url = f"{base_url}/convai/knowledge-base"
all_documents = []
next_cursor = None

print("\n📚 Получение всех документов из Knowledge Base...")

while True:
    params = {}
    if next_cursor:
        params['cursor'] = next_cursor
    
    response = requests.get(kb_url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        documents = data.get('documents', [])
        all_documents.extend(documents)
        
        print(f"   Получено документов на этой странице: {len(documents)}")
        
        # Проверяем, есть ли еще страницы
        if data.get('has_more'):
            next_cursor = data.get('next_cursor')
        else:
            break
    else:
        print(f"❌ Ошибка получения документов: {response.status_code}")
        break

print(f"\n✅ Всего найдено документов: {len(all_documents)}")

# 2. Показываем найденные документы
if all_documents:
    print("\n📄 Список документов:")
    
    # Собираем ID наших документов (MM-RAG и Квартал)
    mmrag_doc_ids = []
    
    for doc in all_documents:
        doc_name = doc.get('name', '')
        doc_id = doc.get('id', '')
        
        # Фильтруем наши документы
        if ('MM-RAG' in doc_name or 
            'Квартал' in doc_name or 
            'Test Document' in doc_name):
            
            print(f"   ✅ {doc_name}")
            print(f"      ID: {doc_id}")
            mmrag_doc_ids.append(doc_id)
    
    print(f"\n📊 Найдено документов MM-RAG: {len(mmrag_doc_ids)}")
    
    if mmrag_doc_ids:
        # 3. Привязываем документы к агенту
        print(f"\n🔧 Привязка {len(mmrag_doc_ids)} документов к агенту...")
        
        agent_url = f"{base_url}/convai/agents/{agent_id}"
        
        # Обновляем агента со всеми документами
        update_data = {
            "knowledge_base": mmrag_doc_ids
        }
        
        response = requests.patch(agent_url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            print("✅ Документы успешно привязаны к агенту!")
            
            # Ждем синхронизацию
            print("\n⏳ Ожидание синхронизации (5 секунд)...")
            time.sleep(5)
            
            # 4. Проверяем результат
            print("\n🔍 Проверка результата:")
            response = requests.get(agent_url, headers=headers)
            
            if response.status_code == 200:
                agent_data = response.json()
                kb_in_agent = agent_data.get('knowledge_base', [])
                
                print(f"✅ Документов в агенте: {len(kb_in_agent)}")
                
                if kb_in_agent:
                    print("\n📚 Документы успешно добавлены в агента!")
                    print("   Первые 5 ID документов в агенте:")
                    for doc_id in kb_in_agent[:5]:
                        print(f"      - {doc_id}")
                    
                    if len(kb_in_agent) > 5:
                        print(f"      ... и еще {len(kb_in_agent) - 5} документов")
                else:
                    print("⚠️ Документы привязаны, но пока не отображаются")
                    print("   Попробуйте проверить через веб-интерфейс ElevenLabs")
        else:
            print(f"❌ Ошибка привязки: {response.status_code}")
            print(f"   Ответ: {response.text}")
    else:
        print("\n⚠️ Не найдено документов MM-RAG для привязки")
else:
    print("\n❌ Knowledge Base пуста")

print("\n" + "=" * 60)
print("✨ Процесс завершен")