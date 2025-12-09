#!/usr/bin/env python3
"""
Инициализация quarters_state.json из текущего состояния агента

Создаёт файл с маппингом: имя квартала → doc_id
Используется для отслеживания какие документы обновлять
"""

import os
import json
import hashlib
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('ELEVENLABS_API_KEY')
AGENT_ID = os.environ.get('ELEVENLABS_AGENT_ID')
BASE_URL = "https://api.elevenlabs.io/v1"

# Список постоянных документов (не обновляем)
PERMANENT_DOCS = [
    'МБА',
    '00-obschie-svedeniya',
    '01-obrazovatelnaya-infrastruktura',
    '02-parkinki-i-sport',
    '03-finansovye-uslugi',
    '03-empathy-enhancer',
    '05-sroki-sdachi-domov',
]


def get_agent_documents():
    """Получить документы из агента"""
    url = f"{BASE_URL}/convai/agents/{AGENT_ID}"
    resp = requests.get(url, headers={"xi-api-key": API_KEY}, timeout=30)
    
    if resp.status_code != 200:
        print(f"❌ Ошибка получения агента: {resp.status_code}")
        return []
    
    data = resp.json()
    kb = data.get('conversation_config', {}).get('agent', {}).get('prompt', {}).get('knowledge_base', [])
    return kb


def calculate_file_hash(file_path: str) -> str:
    """Вычислить MD5 хеш файла"""
    if not Path(file_path).exists():
        return ""
    
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def main():
    print("🔧 Инициализация quarters_state.json\n")
    
    if not API_KEY or not AGENT_ID:
        print("❌ Установите ELEVENLABS_API_KEY и ELEVENLABS_AGENT_ID")
        return
    
    # Получаем документы агента
    print("📥 Получение документов агента...")
    agent_docs = get_agent_documents()
    print(f"   Найдено: {len(agent_docs)} документов\n")
    
    # Создаём state
    state = {
        "last_update": None,
        "permanent_docs": {},
        "quarters": {}
    }
    
    quarters_dir = Path('./quarters')
    
    for doc in agent_docs:
        name = doc.get('name', '')
        doc_id = doc.get('id', '')
        
        # Проверяем MD файл
        md_file = quarters_dir / f"{name}.md"
        content_hash = calculate_file_hash(str(md_file))
        
        doc_info = {
            "doc_id": doc_id,
            "content_hash": content_hash,
            "last_updated": None
        }
        
        if name in PERMANENT_DOCS:
            state["permanent_docs"][name] = doc_info
            print(f"  📌 {name} (постоянный)")
        else:
            state["quarters"][name] = doc_info
            print(f"  🏠 {name} → {doc_id[:20]}...")
    
    # Сохраняем
    state_file = Path('./quarters_state.json')
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Сохранено: {state_file}")
    print(f"   Постоянных: {len(state['permanent_docs'])}")
    print(f"   Кварталов: {len(state['quarters'])}")


if __name__ == "__main__":
    main()

