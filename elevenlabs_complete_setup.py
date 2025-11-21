#!/usr/bin/env python3
"""
Полная настройка ElevenLabs: загрузка документов, индексация RAG и привязка к агенту
"""

import os
import json
import requests
from dotenv import load_dotenv
import time
from typing import Dict, List

load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')
agent_id = os.getenv('ELEVENLABS_AGENT_ID')
base_url = "https://api.elevenlabs.io/v1"

headers = {
    "xi-api-key": api_key,
    "Content-Type": "application/json"
}

def compute_rag_index(doc_id: str, doc_name: str) -> bool:
    """Вычисляет RAG индекс для документа"""
    url = f"{base_url}/convai/knowledge-base/{doc_id}/rag-index"
    
    data = {
        "model": "multilingual_e5_large_instruct"  # Мультиязычная модель для русского текста
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        result = response.json()
        status = result.get('status', 'unknown')
        progress = result.get('progress', 0)
        
        if status == 'indexed':
            print(f"   ✅ {doc_name}: уже проиндексирован")
        elif status == 'created' or status == 'indexing':
            print(f"   🔄 {doc_name}: индексация запущена ({progress}%)")
        else:
            print(f"   ⚠️ {doc_name}: статус {status}")
        
        return True
    else:
        print(f"   ❌ {doc_name}: ошибка индексации {response.status_code}")
        return False

def check_rag_status(doc_id: str) -> str:
    """Проверяет статус RAG индекса"""
    url = f"{base_url}/convai/knowledge-base/{doc_id}/rag-index"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        
        # API возвращает объект с полем indexes
        if isinstance(result, dict) and 'indexes' in result:
            indexes = result.get('indexes', [])
            if indexes and isinstance(indexes, list):
                # Берем статус первого индекса
                return indexes[0].get('status', 'unknown')
        # Старый формат - массив
        elif isinstance(result, list) and result:
            return result[0].get('status', 'unknown')
        # Старый формат - объект
        elif isinstance(result, dict):
            return result.get('status', 'unknown')
    elif response.status_code == 404:
        # Если индекса нет, нужно его создать
        return 'not_found'
    
    return 'error'

def main():
    print("🚀 Полная настройка ElevenLabs Knowledge Base")
    print("=" * 60)
    
    # 1. Получаем список всех документов
    print("\n📚 Получение документов из Knowledge Base...")
    kb_url = f"{base_url}/convai/knowledge-base"
    
    all_documents = []
    next_cursor = None
    
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
    
    print(f"✅ Найдено {len(all_documents)} документов")
    
    # 2. Фильтруем наши документы MM-RAG
    mmrag_docs = []
    
    for doc in all_documents:
        doc_name = doc.get('name', '')
        doc_id = doc.get('id', '')
        
        if ('MM-RAG' in doc_name or 
            'Квартал' in doc_name or 
            'Test Document' in doc_name):
            mmrag_docs.append({
                'id': doc_id,
                'name': doc_name
            })
    
    print(f"\n📊 Найдено {len(mmrag_docs)} документов MM-RAG")
    
    if not mmrag_docs:
        print("❌ Документы MM-RAG не найдены")
        return
    
    # 3. Запускаем индексацию RAG для всех документов
    print("\n🔧 Запуск индексации RAG...")
    
    indexed_docs = []
    
    for doc in mmrag_docs[:10]:  # Индексируем первые 10 для теста
        success = compute_rag_index(doc['id'], doc['name'])
        if success:
            indexed_docs.append(doc)
        time.sleep(0.5)  # Небольшая пауза между запросами
    
    print(f"\n✅ Индексация запущена для {len(indexed_docs)} документов")
    
    # 4. Ждем завершения индексации
    print("\n⏳ Ожидание завершения индексации (до 60 секунд)...")
    
    max_wait = 60  # Максимум 60 секунд
    start_time = time.time()
    check_count = 0
    
    while time.time() - start_time < max_wait:
        all_indexed = True
        pending = []
        statuses = {}
        
        for doc in indexed_docs:
            status = check_rag_status(doc['id'])
            statuses[doc['name']] = status
            if status not in ['indexed', 'succeeded', 'created', 'indexing']:
                all_indexed = False
                pending.append(doc['name'])
        
        check_count += 1
        
        # Показываем статусы первый раз и каждые 3 проверки
        if check_count == 1 or check_count % 3 == 0:
            print(f"\n   Статус документов (проверка {check_count}):")
            for name, status in list(statuses.items())[:5]:  # Показываем первые 5
                print(f"      {name}: {status}")
        
        if all_indexed or not pending:
            print("✅ Индексация завершена или в процессе!")
            break
        else:
            print(f"   Ожидание: {len(pending)} документов не индексируются...")
            time.sleep(5)
    
    # 5. Формируем список для добавления в агента
    print("\n📝 Подготовка документов для агента...")
    
    kb_entries = []
    for doc in indexed_docs:
        # Проверяем финальный статус
        status = check_rag_status(doc['id'])
        
        if status in ['indexed', 'succeeded']:
            kb_entry = {
                "id": doc['id'],
                "name": doc['name'].replace(' ', '-').replace('Квартал-', ''),
                "type": "text",
                "usage_mode": "auto"
            }
            kb_entries.append(kb_entry)
            print(f"   ✅ {doc['name']}: готов к добавлению")
        else:
            print(f"   ⚠️ {doc['name']}: индексация не завершена ({status})")
    
    if not kb_entries:
        print("\n❌ Нет документов готовых к добавлению")
        return
    
    # 6. Обновляем агента
    print(f"\n🤖 Обновление агента с {len(kb_entries)} документами...")
    
    # Получаем текущую конфигурацию
    agent_url = f"{base_url}/convai/agents/{agent_id}"
    response = requests.get(agent_url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Не удалось получить данные агента: {response.status_code}")
        return
    
    agent_data = response.json()
    current_kb = agent_data.get('conversation_config', {}).get('agent', {}).get('prompt', {}).get('knowledge_base', [])
    
    print(f"   Текущих документов: {len(current_kb)}")
    
    # Объединяем существующие и новые документы
    existing_ids = {doc['id'] for doc in current_kb}
    
    for new_doc in kb_entries:
        if new_doc['id'] not in existing_ids:
            current_kb.append(new_doc)
    
    # Обновляем агента
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
        print(f"✅ Агент обновлен! Всего документов: {len(current_kb)}")
    else:
        print(f"❌ Ошибка обновления: {response.status_code}")
        error_detail = response.json().get('detail', {})
        if 'rag_index_not_ready' in str(error_detail):
            print("   Некоторые документы еще не проиндексированы")
            print("   Попробуйте запустить скрипт позже")
        else:
            print(f"   Детали: {response.text[:500]}")
    
    print("\n" + "=" * 60)
    print("✨ Процесс завершен")
    print("\nРекомендации:")
    print("1. Если не все документы добавлены, подождите 1-2 минуты")
    print("2. Запустите скрипт повторно для добавления оставшихся")
    print("3. Проверьте агента через веб-интерфейс ElevenLabs")


if __name__ == "__main__":
    main()