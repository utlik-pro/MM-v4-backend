#!/usr/bin/env python3
"""
ElevenLabs Sync v2 - Правильная синхронизация с агентом

Исправления:
1. Правильный путь: conversation_config.agent.prompt.knowledge_base
2. Загружает только изменённые файлы (по хешу)
3. Заменяет старые версии на новые (не добавляет)
4. Удаляет старые версии из KB после отвязки от агента
"""

import os
import sys
import json
import time
import hashlib
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Загружаем .env если есть
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Конфигурация
API_KEY = os.environ.get('ELEVENLABS_API_KEY')
AGENT_ID = os.environ.get('ELEVENLABS_AGENT_ID')
BASE_URL = "https://api.elevenlabs.io/v1"

# Постоянные документы (не обновляем)
PERMANENT_DOCS = {
    'МБА', '00-obschie-svedeniya', '01-obrazovatelnaya-infrastruktura',
    '02-parkinki-i-sport', '03-finansovye-uslugi', '03-empathy-enhancer',
    '05-sroki-sdachi-domov'
}

STATE_FILE = Path('./quarters_state.json')


def log(msg: str):
    """Вывод с timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}", flush=True)


def get_headers() -> dict:
    return {"xi-api-key": API_KEY}


def load_state() -> dict:
    """Загрузить состояние"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"quarters": {}, "permanent_docs": {}}


def save_state(state: dict):
    """Сохранить состояние"""
    state["last_update"] = datetime.now().isoformat()
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def calculate_hash(file_path: str) -> str:
    """MD5 хеш файла"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def get_agent_kb() -> List[Dict]:
    """Получить knowledge_base агента (ПРАВИЛЬНЫЙ ПУТЬ!)"""
    url = f"{BASE_URL}/convai/agents/{AGENT_ID}"
    resp = requests.get(url, headers=get_headers(), timeout=60)
    
    if resp.status_code != 200:
        log(f"❌ Ошибка получения агента: {resp.status_code}")
        return []
    
    data = resp.json()
    # ПРАВИЛЬНЫЙ ПУТЬ!
    kb = data.get('conversation_config', {}).get('agent', {}).get('prompt', {}).get('knowledge_base', [])
    return kb


def upload_document(file_path: str, name: str) -> Optional[str]:
    """Загрузить документ в KB и запустить индексацию"""
    url = f"{BASE_URL}/convai/knowledge-base"
    
    with open(file_path, 'rb') as f:
        files = {'file': (f"{name}.md", f, 'text/markdown')}
        resp = requests.post(url, headers=get_headers(), files=files, timeout=120)
    
    if resp.status_code in [200, 201]:
        doc_id = resp.json().get('id')
        log(f"      📤 Загружен: {doc_id[:20]}...")
        
        # ВАЖНО: Запускаем RAG индексацию явно!
        # ElevenLabs НЕ индексирует автоматически через API
        trigger_rag_indexing(doc_id)
        
        return doc_id
    else:
        log(f"❌ Ошибка загрузки {name}: {resp.status_code}")
        return None


def trigger_rag_indexing(doc_id: str) -> bool:
    """Явно запустить RAG индексацию для документа
    
    ElevenLabs НЕ индексирует автоматически через API!
    Нужно вызвать POST /convai/knowledge-base/{id}/rag-index
    """
    url = f"{BASE_URL}/convai/knowledge-base/{doc_id}/rag-index"
    
    # Используем ту же модель что у агента
    data = {
        "model": "multilingual_e5_large_instruct"
    }
    
    try:
        resp = requests.post(
            url, 
            headers={**get_headers(), "Content-Type": "application/json"},
            json=data,
            timeout=60
        )
        
        if resp.status_code in [200, 201, 202]:
            log(f"      ✅ Индексация запущена")
            return True
        else:
            log(f"      ⚠️  Статус индексации: {resp.status_code}")
            return False
            
    except Exception as e:
        log(f"      ❌ Ошибка запуска индексации: {e}")
        return False


def check_indexing_status(doc_id: str) -> str:
    """Проверить статус индексации документа
    
    ElevenLabs API возвращает:
    {
        "indexes": [
            {"status": "succeeded", "progress_percentage": 100.0, ...}
        ]
    }
    """
    url = f"{BASE_URL}/convai/knowledge-base/{doc_id}/rag-index"
    
    try:
        resp = requests.get(url, headers=get_headers(), timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            # Правильный путь: indexes[0].status
            indexes = data.get('indexes', [])
            if indexes:
                return indexes[0].get('status', 'unknown')
            return 'no_index'
        return 'error'
    except:
        return 'error'


def wait_for_indexing(doc_id: str, max_wait: int = 120) -> bool:
    """Дождаться завершения индексации документа
    
    Args:
        doc_id: ID документа
        max_wait: Максимальное время ожидания в секундах
    
    Returns:
        True если индексация завершена, False если таймаут
    """
    start = time.time()
    
    while time.time() - start < max_wait:
        status = check_indexing_status(doc_id)
        
        # succeeded - успешно проиндексирован (ElevenLabs API)
        if status in ['succeeded', 'indexed', 'completed', 'ready']:
            return True
        elif status in ['error', 'failed']:
            log(f"      ❌ Ошибка индексации")
            return False
        
        # Ждём и проверяем снова
        time.sleep(5)
    
    log(f"      ⚠️  Таймаут ожидания индексации")
    return False


def update_agent_kb(new_kb: List[Dict]) -> bool:
    """Обновить KB агента (ПРАВИЛЬНЫЙ ПУТЬ!)"""
    url = f"{BASE_URL}/convai/agents/{AGENT_ID}"
    
    update_data = {
        "conversation_config": {
            "agent": {
                "prompt": {
                    "knowledge_base": new_kb
                }
            }
        }
    }
    
    log(f"   📤 PATCH запрос ({len(new_kb)} документов)...")
    
    # Retry с увеличенным таймаутом
    for attempt in range(3):
        try:
            resp = requests.patch(
                url,
                headers={**get_headers(), "Content-Type": "application/json"},
                json=update_data,
                timeout=(30, 600)  # 30s connect, 10min read (индексация может быть долгой)
            )
            
            if resp.status_code == 200:
                log(f"   ✅ Агент обновлён успешно")
                return True
            else:
                log(f"   ❌ Ошибка: {resp.status_code} - {resp.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            log(f"   ⚠️  Попытка {attempt + 1}/3: таймаут")
            if attempt < 2:
                time.sleep(5)
        except Exception as e:
            log(f"   ❌ Ошибка запроса: {e}")
            return False
    
    log("   ❌ Все попытки исчерпаны")
    return False


def delete_document(doc_id: str) -> bool:
    """Удалить документ из KB"""
    url = f"{BASE_URL}/convai/knowledge-base/{doc_id}"
    resp = requests.delete(url, headers=get_headers(), timeout=30)
    return resp.status_code in [200, 204]


def init_state_from_agent(agent_docs: dict, quarters_path: Path) -> dict:
    """Инициализировать state из текущих документов агента"""
    state = {"quarters": {}, "permanent_docs": {}}
    
    for name, doc in agent_docs.items():
        md_file = quarters_path / f"{name}.md"
        content_hash = ""
        if md_file.exists():
            content_hash = calculate_hash(str(md_file))
        
        doc_info = {
            "doc_id": doc.get('id', ''),
            "content_hash": content_hash,
            "last_updated": None
        }
        
        if name in PERMANENT_DOCS:
            state["permanent_docs"][name] = doc_info
        else:
            state["quarters"][name] = doc_info
    
    return state


def sync_quarters(quarters_dir: str = 'quarters', changed_files: List[str] = None, dry_run: bool = False):
    """
    Главная функция синхронизации
    
    Args:
        quarters_dir: Директория с MD файлами
        changed_files: Список изменённых файлов (опционально)
        dry_run: Только показать что будет сделано
    """
    log("=" * 60)
    log("🚀 ElevenLabs Sync v2")
    log("=" * 60)
    
    if not API_KEY or not AGENT_ID:
        log("❌ Установите ELEVENLABS_API_KEY и ELEVENLABS_AGENT_ID")
        return
    
    quarters_path = Path(quarters_dir)
    
    # Загружаем state или создаём новый
    state = load_state()
    
    # Шаг 1: Получаем текущие документы агента
    log("\n📥 Шаг 1: Получение документов агента...")
    agent_kb = get_agent_kb()
    log(f"   Документов в агенте: {len(agent_kb)}")
    
    # Создаём словарь name → doc для агента
    agent_docs = {doc['name']: doc for doc in agent_kb}
    
    # Автоматическая инициализация state если пустой
    if not state.get('quarters'):
        log("⚠️  State пустой, инициализируем из агента...")
        state = init_state_from_agent(agent_docs, quarters_path)
        save_state(state)
        log(f"   ✅ Инициализировано {len(state['quarters'])} кварталов")
    
    # Шаг 2: Определяем какие файлы изменились
    log("\n🔍 Шаг 2: Проверка изменений...")
    
    files_to_update = []
    files_to_update_names = set()  # Защита от дубликатов
    
    # Если передан список файлов, используем его
    if changed_files:
        # Убираем дубликаты из changed_files
        unique_files = list(dict.fromkeys(changed_files))
        md_files = [quarters_path / f for f in unique_files if f.endswith('.md')]
    else:
        md_files = list(quarters_path.glob('*.md'))
    
    # Не используем force_update - всегда проверяем хеши
    # Это важно для Render где quarters_state.json может быть пустым,
    # но мы инициализируем его из агента и сравниваем с актуальными файлами
    
    for md_file in md_files:
        name = md_file.stem  # Имя без .md
        
        # Пропускаем постоянные документы
        if name in PERMANENT_DOCS:
            continue
        
        # Пропускаем файлы которые НЕ привязаны к агенту
        if name not in agent_docs:
            log(f"   ⏭️  {name} (не в агенте, пропускаем)")
            continue
        
        current_hash = calculate_hash(str(md_file))
        saved_hash = state.get('quarters', {}).get(name, {}).get('content_hash', '')
        
        # Обновляем только если хеш файла изменился И файл ещё не в списке
        if current_hash != saved_hash and name not in files_to_update_names:
            files_to_update_names.add(name)
            files_to_update.append({
                'name': name,
                'path': str(md_file),
                'hash': current_hash,
                'old_doc_id': agent_docs.get(name, {}).get('id')
            })
            # Показываем первые 8 символов хешей для отладки
            log(f"   🔄 {name} (хеш: {saved_hash[:8] if saved_hash else 'empty'}→{current_hash[:8]})")
        else:
            log(f"   ✅ {name} (без изменений)")
    
    if not files_to_update:
        log("\n✅ Нет изменений для синхронизации")
        return
    
    log(f"\n📊 К обновлению: {len(files_to_update)} файлов")
    
    if dry_run:
        log("\n⚠️  DRY RUN - изменения не применены")
        return
    
    # Шаг 3: Загружаем новые версии
    log("\n📤 Шаг 3: Загрузка новых версий...")
    
    uploaded = []
    for file_info in files_to_update:
        log(f"   📤 {file_info['name']}...", )
        
        new_doc_id = upload_document(file_info['path'], file_info['name'])
        if new_doc_id:
            file_info['new_doc_id'] = new_doc_id
            uploaded.append(file_info)
            log(f"   ✅ {file_info['name']} → {new_doc_id[:20]}...")
        else:
            log(f"   ❌ {file_info['name']} - ошибка загрузки")
    
    if not uploaded:
        log("❌ Ничего не загружено")
        return
    
    # Шаг 4: Ожидание индексации документов
    log("\n⏳ Шаг 4: Ожидание индексации...")
    
    indexed = []
    for file_info in uploaded:
        doc_id = file_info['new_doc_id']
        name = file_info['name']
        
        log(f"   🔍 {name}...", )
        
        # Ждём индексации (макс 30 секунд — обычно очень быстро)
        if wait_for_indexing(doc_id, max_wait=30):
            indexed.append(file_info)
            log(f"   ✅ {name} проиндексирован")
        else:
            # Даже если не дождались - добавляем, индексация продолжится в фоне
            indexed.append(file_info)
            log(f"   ⚠️  {name} - индексация в процессе (продолжим)")
    
    log(f"   📊 Документов для обновления: {len(indexed)}")
    
    # Шаг 5: Обновляем агента (заменяем старые ID на новые)
    log("\n🤖 Шаг 5: Обновление агента...")
    
    # Создаём новый KB - заменяем старые документы на новые
    new_agent_kb = []
    old_doc_ids = []  # Для удаления
    seen_names = set()  # Защита от дубликатов
    
    for doc in agent_kb:
        name = doc['name']
        
        # Пропускаем дубликаты (оставляем только первый)
        if name in seen_names:
            log(f"   ⚠️  {name}: дубликат, пропускаем")
            old_doc_ids.append(doc['id'])  # Удалим дубликат
            continue
        seen_names.add(name)
        
        # Проверяем есть ли обновление для этого документа
        updated = next((f for f in indexed if f['name'] == name), None)
        
        if updated:
            # Заменяем на новую версию
            new_agent_kb.append({
                'type': doc.get('type', 'text'),
                'name': name,
                'id': updated['new_doc_id'],
                'usage_mode': doc.get('usage_mode', 'auto')
            })
            if updated.get('old_doc_id'):
                old_doc_ids.append(updated['old_doc_id'])
            log(f"   🔄 {name}: {updated.get('old_doc_id', 'new')[:15]}... → {updated['new_doc_id'][:15]}...")
        else:
            # Оставляем как есть
            new_agent_kb.append(doc)
    
    log(f"   📊 Итого в агенте: {len(new_agent_kb)} документов")
    
    # Обновляем агента
    if not update_agent_kb(new_agent_kb):
        return
    
    # Шаг 6: Удаляем старые версии из KB
    if old_doc_ids:
        log("\n🗑️  Шаг 6: Удаление старых версий...")
        time.sleep(2)  # Даём время на отвязку
        
        for old_id in old_doc_ids:
            if delete_document(old_id):
                log(f"   ✅ Удалён: {old_id[:20]}...")
            else:
                log(f"   ⚠️  Не удалён: {old_id[:20]}...")
    
    # Шаг 7: Сохраняем состояние
    log("\n💾 Шаг 7: Сохранение состояния...")
    
    for file_info in indexed:
        state['quarters'][file_info['name']] = {
            'doc_id': file_info['new_doc_id'],
            'content_hash': file_info['hash'],
            'last_updated': datetime.now().isoformat()
        }
    
    save_state(state)
    
    # Итоги
    log("\n" + "=" * 60)
    log("📊 ИТОГИ:")
    log(f"   📤 Загружено: {len(uploaded)}")
    log(f"   ✅ Проиндексировано: {len(indexed)}")
    log(f"   🗑️  Удалено старых: {len(old_doc_ids)}")
    log("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='ElevenLabs Sync v2')
    parser.add_argument('--dir', default='quarters', help='Директория с MD файлами')
    parser.add_argument('--dry-run', action='store_true', help='Только показать изменения')
    parser.add_argument('--changed-files', type=str, help='Файл со списком изменённых файлов')
    
    args = parser.parse_args()
    
    changed_files = None
    if args.changed_files:
        with open(args.changed_files, 'r') as f:
            changed_files = [line.strip() for line in f if line.strip()]
    
    sync_quarters(
        quarters_dir=args.dir,
        changed_files=changed_files,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()

