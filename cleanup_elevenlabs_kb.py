#!/usr/bin/env python3
"""
🧹 Скрипт очистки ElevenLabs Knowledge Base от дубликатов

Удаляет все старые версии документов, оставляя только самую новую
версию каждого квартала.

Использование:
    python cleanup_elevenlabs_kb.py --dry-run   # Показать что будет удалено
    python cleanup_elevenlabs_kb.py --execute   # Выполнить удаление
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# Конфигурация
API_KEY = os.environ.get('ELEVENLABS_API_KEY')
BASE_URL = "https://api.elevenlabs.io/v1"

def log(msg):
    """Вывод с временной меткой"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")
    sys.stdout.flush()

def get_all_kb_documents():
    """Получить все документы из Knowledge Base"""
    all_docs = []
    page = 0
    max_pages = 200  # До 20,000 документов
    
    log("📥 Получение списка документов из KB...")
    
    while page < max_pages:
        url = f"{BASE_URL}/convai/knowledge-base?page_size=100&page={page}"
        
        try:
            response = requests.get(
                url, 
                headers={"xi-api-key": API_KEY}, 
                timeout=60
            )
            
            if response.status_code != 200:
                log(f"❌ HTTP {response.status_code} на странице {page}")
                break
            
            data = response.json()
            docs = data.get('documents', data.get('knowledge_bases', []))
            
            if not docs:
                log(f"✅ Все документы получены (страница {page})")
                break
            
            all_docs.extend(docs)
            
            if page % 10 == 0:
                log(f"   📄 Страница {page}: всего {len(all_docs)} документов")
            
            has_more = data.get('has_more', False)
            if not has_more:
                break
            
            page += 1
            time.sleep(0.3)  # Rate limiting
            
        except Exception as e:
            log(f"❌ Ошибка на странице {page}: {e}")
            break
    
    log(f"📊 Всего документов в KB: {len(all_docs)}")
    return all_docs

def analyze_documents(all_docs):
    """Анализ документов - найти дубликаты"""
    grouped = defaultdict(list)
    
    # Группировка по базовому имени
    for doc in all_docs:
        name = doc.get('name', '')
        
        # Пропускаем системные
        if any(x in name.lower() for x in ['system', 'prompt', 'elevenlabs_rag']):
            continue
        
        # Базовое имя (без дат и версий)
        import re
        base_name = re.sub(r'-v\d+|-\d{4}-\d{2}-\d{2}', '', name)
        base_name = re.sub(r'\.(txt|md|html)$', '', base_name)
        
        # Получаем дату создания
        metadata = doc.get('metadata', {})
        created = metadata.get('created_at_unix_secs', 0)
        
        grouped[base_name].append({
            'id': doc.get('id'),
            'name': name,
            'created': created,
            'created_str': datetime.fromtimestamp(created).strftime('%Y-%m-%d %H:%M:%S') if created else 'unknown'
        })
    
    # Определяем что оставить и что удалить
    to_keep = []
    to_delete = []
    
    for base_name, versions in grouped.items():
        # Сортируем по дате (новые первые)
        versions_sorted = sorted(versions, key=lambda x: x['created'], reverse=True)
        
        # Первый (самый новый) - оставляем
        if versions_sorted:
            to_keep.append(versions_sorted[0])
        
        # Остальные - удаляем
        for v in versions_sorted[1:]:
            to_delete.append(v)
    
    return to_keep, to_delete, grouped

def delete_document(doc_id):
    """Удалить один документ"""
    url = f"{BASE_URL}/convai/knowledge-base/{doc_id}"
    
    try:
        response = requests.delete(
            url,
            headers={"xi-api-key": API_KEY},
            timeout=30
        )
        return response.status_code in [200, 204]
    except Exception as e:
        log(f"❌ Ошибка удаления {doc_id}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Очистка ElevenLabs KB от дубликатов')
    parser.add_argument('--dry-run', action='store_true', help='Только показать что будет удалено')
    parser.add_argument('--execute', action='store_true', help='Выполнить удаление')
    parser.add_argument('--batch-size', type=int, default=50, help='Размер батча для удаления')
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("Укажите --dry-run или --execute")
        print("  --dry-run  - показать что будет удалено")
        print("  --execute  - выполнить удаление")
        sys.exit(1)
    
    if not API_KEY:
        log("❌ ELEVENLABS_API_KEY не установлен!")
        sys.exit(1)
    
    log("🧹 Очистка ElevenLabs Knowledge Base")
    log("=" * 60)
    
    # Получаем все документы
    all_docs = get_all_kb_documents()
    
    if not all_docs:
        log("ℹ️  Документы не найдены")
        return
    
    # Анализируем
    to_keep, to_delete, grouped = analyze_documents(all_docs)
    
    log("")
    log("=" * 60)
    log("📊 АНАЛИЗ:")
    log(f"   📚 Всего документов: {len(all_docs)}")
    log(f"   ✅ Оставить (уникальных): {len(to_keep)}")
    log(f"   🗑️  Удалить (дубликатов): {len(to_delete)}")
    log("")
    
    # Показываем группы с дубликатами
    log("📋 Группы с дубликатами:")
    for base_name, versions in sorted(grouped.items()):
        if len(versions) > 1:
            log(f"   {base_name}: {len(versions)} версий")
            for i, v in enumerate(sorted(versions, key=lambda x: x['created'], reverse=True)[:3]):
                marker = "✅" if i == 0 else "🗑️"
                log(f"      {marker} {v['name']} ({v['created_str']})")
            if len(versions) > 3:
                log(f"      ... и еще {len(versions) - 3} версий")
    
    if args.dry_run:
        log("")
        log("=" * 60)
        log("🔍 DRY RUN - удаление не выполнено")
        log(f"   Для удаления запустите: python cleanup_elevenlabs_kb.py --execute")
        return
    
    # Выполняем удаление
    if args.execute:
        log("")
        log("=" * 60)
        log(f"🗑️  УДАЛЕНИЕ {len(to_delete)} документов...")
        log("")
        
        # Подтверждение
        confirm = input(f"Вы уверены? Будет удалено {len(to_delete)} документов! (yes/no): ")
        if confirm.lower() != 'yes':
            log("❌ Отменено")
            return
        
        deleted = 0
        failed = 0
        
        for i, doc in enumerate(to_delete, 1):
            success = delete_document(doc['id'])
            
            if success:
                deleted += 1
            else:
                failed += 1
            
            # Прогресс каждые 50 документов
            if i % args.batch_size == 0:
                log(f"   Прогресс: {i}/{len(to_delete)} (удалено: {deleted}, ошибок: {failed})")
                time.sleep(1)  # Пауза между батчами
            else:
                time.sleep(0.2)  # Пауза между запросами
        
        log("")
        log("=" * 60)
        log("✅ ГОТОВО!")
        log(f"   Удалено: {deleted}")
        log(f"   Ошибок: {failed}")
        log(f"   Осталось документов: ~{len(to_keep)}")

if __name__ == "__main__":
    main()

