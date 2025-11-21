#!/usr/bin/env python3
"""
Скрипт для добавления документов к агенту ElevenLabs
Использует прямой API вызов для привязки документов
"""

import os
import json
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def get_all_knowledge_bases():
    """Получить все документы из Knowledge Base"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    headers = {'xi-api-key': api_key}

    all_docs = []
    page = 0

    while True:
        url = f"https://api.elevenlabs.io/v1/convai/knowledge-base?page_size=100&page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Ошибка получения документов: {response.status_code}")
            break

        data = response.json()
        docs = data.get('knowledge_bases', [])

        if not docs:
            break

        all_docs.extend(docs)

        if not data.get('has_more', False):
            break

        page += 1

    return all_docs


def add_documents_to_agent_one_by_one():
    """Добавляет документы к агенту по одному"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')

    headers = {
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }

    # Читаем ID загруженных документов из файла
    uploaded_ids_file = '/Users/admin/MM-RAG/uploaded_kb_ids.txt'
    if os.path.exists(uploaded_ids_file):
        with open(uploaded_ids_file, 'r') as f:
            new_kb_ids = [line.strip() for line in f.readlines() if line.strip()]
        print(f"📚 Загружено {len(new_kb_ids)} ID из uploaded_kb_ids.txt")
    else:
        print("📚 Получение списка документов из API...")
        all_docs = get_all_knowledge_bases()
        fresh_docs = all_docs[:20]
        new_kb_ids = [doc['knowledge_base_id'] for doc in fresh_docs]
        print(f"✅ Найдено {len(new_kb_ids)} свежих документов")

    print(f"\n🔧 Добавление {len(new_kb_ids)} документов к агенту...")

    # Получаем текущую конфигурацию агента
    agent_url = f"https://api.elevenlabs.io/v1/convai/agents/{agent_id}"
    response = requests.get(agent_url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Не удалось получить конфигурацию агента: {response.status_code}")
        return False

    agent_config = response.json()
    # knowledge_base находится в root объекта агента
    current_kb = agent_config.get('knowledge_base', [])

    print(f"📊 Текущих документов в агенте: {len(current_kb)}")

    # Объединяем со старыми (убираем дубликаты)
    all_kb_ids = list(set(current_kb + new_kb_ids))

    print(f"📊 Итого будет документов: {len(all_kb_ids)}")

    # Обновляем агента - knowledge_base в root
    update_data = {
        "knowledge_base": all_kb_ids
    }

    print("\n🔄 Отправка обновления агенту...")
    response = requests.patch(agent_url, headers=headers, json=update_data, timeout=60)

    if response.status_code == 200:
        print("✅ Документы успешно добавлены к агенту!")

        # Проверяем результат
        response = requests.get(agent_url, headers=headers)
        if response.status_code == 200:
            agent_config = response.json()
            final_kb = agent_config.get('knowledge_base', [])
            print(f"✅ Подтверждение: в агенте теперь {len(final_kb)} документов")

        return True
    else:
        print(f"❌ Ошибка при обновлении агента: {response.status_code}")
        print(f"Ответ: {response.text}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔗 Добавление документов к агенту ElevenLabs")
    print("=" * 60)

    try:
        success = add_documents_to_agent_one_by_one()

        if success:
            print("\n" + "=" * 60)
            print("✨ Готово! Агент обновлен с новыми документами")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ Не удалось обновить агента")
            print("=" * 60)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
