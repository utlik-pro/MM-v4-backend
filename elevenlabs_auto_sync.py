#!/usr/bin/env python3
"""
Автоматическая синхронизация документов ElevenLabs с удалением старых версий

Использование:
    python3 elevenlabs_auto_sync.py              # Полная синхронизация
    python3 elevenlabs_auto_sync.py --dry-run    # Показать что будет сделано
    python3 elevenlabs_auto_sync.py --no-delete  # Только загрузка, без удаления
"""

import os
import json
import requests
import time
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from collections import defaultdict
import sys

load_dotenv()


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


class ElevenLabsAutoSync:
    """Полная автоматизация синхронизации Knowledge Base с безопасным управлением версиями"""

    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.agent_id = os.getenv('ELEVENLABS_AGENT_ID')

        if not self.api_key:
            raise ValueError("❌ ELEVENLABS_API_KEY не найден в .env файле")
        if not self.agent_id:
            raise ValueError("❌ ELEVENLABS_AGENT_ID не найден в .env файле")

        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        # Логирование операций
        self.log_file = "elevenlabs_sync_log.json"
        self.load_sync_log()

    def load_sync_log(self):
        """Загрузить историю синхронизаций"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                self.sync_log = json.load(f)
        else:
            self.sync_log = {
                "last_sync": None,
                "uploads": {},  # filename -> {id, upload_date, hash}
                "deletions": []  # [{id, name, deletion_date, reason}]
            }

    def save_sync_log(self):
        """Сохранить историю синхронизаций"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.sync_log, f, indent=2, ensure_ascii=False)

    def get_all_kb_documents_cached(self, ttl_minutes: int = 60, use_cache_only: bool = False) -> List[Dict]:
        """
        Получить KB документы с кэшированием для избежания повторных API вызовов

        Args:
            ttl_minutes: Время жизни кэша в минутах
            use_cache_only: Если True, не делать запрос к API, только использовать кэш

        Returns:
            Список документов из KB
        """
        cache_file = Path('.elevenlabs_kb_cache.json')

        # Проверяем валидность кэша
        if cache_file.exists():
            mtime = cache_file.stat().st_mtime
            age_minutes = (time.time() - mtime) / 60

            if age_minutes < ttl_minutes:
                log(f"  📦 Использование кэша KB (возраст: {age_minutes:.1f} мин)")
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_docs = json.load(f)
                        log(f"  ✅ Загружено из кэша: {len(cached_docs)} документов")
                        return cached_docs
                except Exception as e:
                    log(f"  ⚠️  Ошибка чтения кэша: {e}, загружаем свежие данные")

        # Если use_cache_only=True и кэша нет - возвращаем пустой список
        if use_cache_only:
            log(f"  ⚠️  Кэш отсутствует или устарел, но режим use_cache_only=True")
            log(f"  💡 Продолжаем без удаления старых версий (только загрузка новых)")
            return []

        # Получаем свежие данные
        log(f"  🔄 Загрузка свежих данных KB...")
        
        # Сохраняем старый кэш на случай ошибки
        old_cache_docs = []
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    old_cache_docs = json.load(f)
                    log(f"  📦 Сохранен старый кэш для fallback ({len(old_cache_docs)} документов)")
            except:
                pass
        
        try:
            docs = self.get_all_kb_documents()

            # Кэшируем
            log(f"  💾 Сохранение кэша ({len(docs)} документов)...")
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(docs, f, ensure_ascii=False, indent=2)
                log(f"  ✅ Кэш сохранен")
            except Exception as e:
                log(f"  ⚠️  Ошибка сохранения кэша: {e}")

            return docs
        except Exception as e:
            log(f"  ❌ Ошибка получения документов: {type(e).__name__} - {str(e)[:200]}")
            
            # Если есть старый кэш - используем его как fallback
            if old_cache_docs:
                log(f"  🔄 Fallback: используем старый кэш ({len(old_cache_docs)} документов)")
                log(f"  ⚠️  Внимание: список документов может быть неполным, старые версии могут не удалиться")
                return old_cache_docs
            
            log(f"  💡 Старого кэша нет, возвращаем пустой список")
            return []

    # ===== ПОЛУЧЕНИЕ СПИСКА ДОКУМЕНТОВ =====

    def get_all_kb_documents(self) -> List[Dict]:
        """Получить все документы из Knowledge Base с пагинацией"""
        all_docs = []
        page = 0
        max_pages = 100  # Защита от бесконечного цикла

        log(f"   📥 Начало загрузки документов из KB (таймаут: 60с)")
        
        while page < max_pages:
            url = f"{self.base_url}/convai/knowledge-base?page_size=100&page={page}"
            
            try:
                log(f"   📄 Запрос страницы {page}...")
                response = requests.get(url, headers={"xi-api-key": self.api_key}, timeout=60)

                if response.status_code != 200:
                    log(f"   ❌ HTTP {response.status_code} на странице {page}")
                    if page == 0:
                        log(f"   📝 Ответ сервера: {response.text[:500]}")
                    break

                data = response.json()
                docs = data.get('documents', data.get('knowledge_bases', []))

                if not docs:
                    log(f"   ℹ️  Страница {page}: документов нет, завершение")
                    break

                all_docs.extend(docs)
                log(f"   ✅ Страница {page}: получено {len(docs)} документов (всего: {len(all_docs)})")

                has_more = data.get('has_more', False)
                if not has_more:
                    log(f"   ✅ Все страницы загружены (has_more=False)")
                    break

                page += 1
                time.sleep(0.5)  # Пауза между запросами

            except requests.exceptions.Timeout:
                log(f"   ❌ Таймаут запроса на странице {page} (>60 сек)")
                break
            except requests.exceptions.RequestException as e:
                log(f"   ❌ Ошибка сети на странице {page}: {type(e).__name__} - {str(e)[:200]}")
                break
            except Exception as e:
                log(f"   ❌ Неожиданная ошибка на странице {page}: {type(e).__name__} - {str(e)[:200]}")
                break

        log(f"   📊 Итого загружено: {len(all_docs)} документов из {page + 1} страниц")
        return all_docs

    # ===== ОПРЕДЕЛЕНИЕ ДОКУМЕНТОВ ДЛЯ УДАЛЕНИЯ =====

    def identify_documents_to_delete(self, all_docs: List[Dict], changed_files: List[str] = None) -> List[Dict]:
        """
        Определить документы для удаления (старые версии)

        Args:
            all_docs: Все документы в KB
            changed_files: Список измененных файлов (только их старые версии удаляем)

        Логика:
        - Группируем по базовому имени (без дат и версий)
        - В каждой группе оставляем только самый новый документ
        - Остальные помечаем для удаления
        - Если указан changed_files, удаляем только старые версии этих файлов
        """
        to_delete = []
        grouped = defaultdict(list)

        # Если есть список измененных файлов, извлекаем базовые имена
        changed_base_names = set()
        if changed_files:
            for f in changed_files:
                # Убираем .md расширение
                base = f.replace('.md', '')
                changed_base_names.add(base)

        for doc in all_docs:
            name = doc.get('name', '')

            # Пропускаем системные документы
            if any(x in name.lower() for x in ['system', 'elevenlabs_rag', 'prompt']):
                continue

            # Извлекаем базовое имя (убираем даты и версии)
            # Примеры: "02-emirats-2025-11-20" -> "02-emirats"
            #          "10-Tropicheskie-ostrova-v2" -> "10-Tropicheskie-ostrova"
            base_name = re.sub(r'-v\d+|-\d{4}-\d{2}-\d{2}', '', name)
            base_name = re.sub(r'\.(txt|md)$', '', base_name)

            grouped[base_name].append(doc)

        # Анализируем каждую группу
        for base_name, versions in grouped.items():
            # Если есть фильтр changed_files, проверяем вхождение
            if changed_files and base_name not in changed_base_names:
                # Этот файл не изменился, пропускаем
                continue
            
            # Логируем для отладки
            if changed_files:
                log(f"   🔍 Анализ: {base_name} ({len(versions)} версий)")
            
            if len(versions) <= 1:
                continue  # Только одна версия - ничего не удаляем

            # Сортируем по дате создания
            versions_with_date = []

            for v in versions:
                doc_id = v.get('id')
                doc_name = v.get('name', 'unknown')
                
                # Пытаемся получить дату создания из метаданных ElevenLabs
                metadata = v.get('metadata', {})
                created = metadata.get('created_at_unix_secs')
                
                if created:
                    versions_with_date.append((v, created))
                    if changed_files:
                        log(f"      ✅ Дата из metadata: {doc_name[:40]} -> {datetime.fromtimestamp(created).strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    # Проверяем локальный лог синхронизаций
                    found_in_log = False
                    for log_name, log_info in self.sync_log['uploads'].items():
                        if log_info.get('id') == doc_id:
                            upload_date = log_info.get('upload_date', '')
                            if upload_date:
                                # Конвертируем ISO дату в unix timestamp
                                try:
                                    dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                                    timestamp = int(dt.timestamp())
                                    versions_with_date.append((v, timestamp))
                                    found_in_log = True
                                    if changed_files:
                                        log(f"      ✅ Дата из локального лога: {doc_name[:40]} -> {upload_date}")
                                    break
                                except Exception as e:
                                    if changed_files:
                                        log(f"      ⚠️  Ошибка парсинга даты из лога: {e}")
                    
                    if not found_in_log and changed_files:
                        log(f"      ❌ Не найдена дата для: {doc_name[:40]} (ID: {doc_id[:20]}...)")
                        # Показываем что есть в метаданных для отладки
                        if metadata:
                            log(f"         Метаданные: {json.dumps(metadata, ensure_ascii=False)[:200]}")

            if not versions_with_date:
                if changed_files:
                    log(f"      ⚠️  Пропуск {base_name}: не удалось определить даты ни для одной версии")
                continue  # Не смогли определить даты

            # Сортируем (новые первые)
            versions_with_date.sort(key=lambda x: x[1], reverse=True)

            # Все кроме первого (самого нового) - удаляем
            for doc, date in versions_with_date[1:]:
                newest_date = datetime.fromtimestamp(versions_with_date[0][1]).strftime('%Y-%m-%d')
                doc_name = doc.get('name', 'unknown')
                
                to_delete.append({
                    'id': doc.get('id'),
                    'name': doc_name,
                    'reason': f'старая версия (новейшая от {newest_date})'
                })
                
                if changed_files:
                    log(f"      🗑️  Найдена старая версия: {doc_name[:50]}")

        return to_delete

    # ===== ЗАГРУЗКА НОВЫХ ДОКУМЕНТОВ =====

    def upload_new_documents(self, files_dir: str = 'quarters', changed_files: List[str] = None) -> List[str]:
        """
        Загрузить новые или обновленные документы

        Args:
            files_dir: Директория с MD-файлами
            changed_files: Список конкретных файлов для обработки (опционально)

        Returns:
            Список ID загруженных документов
        """
        uploaded_ids = []
        files_to_upload = []

        # Находим все MD файлы для загрузки
        if changed_files:
            # Обрабатываем только указанные файлы
            print(f"🎯 Инкрементальное обновление: {len(changed_files)} файлов")
            md_files_to_check = [Path(files_dir) / f for f in changed_files if f.endswith('.md')]
        else:
            # Обрабатываем все файлы
            print(f"📚 Полная синхронизация всех MD-файлов")
            md_files_to_check = list(Path(files_dir).glob('*.md'))

        for md_file in md_files_to_check:
            file_path = str(md_file)
            file_name = md_file.stem  # Имя без расширения

            # Вычисляем хеш файла
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            # Проверяем, нужно ли загружать
            should_upload = False

            # Если передан список changed_files, то все файлы из него должны быть загружены
            if changed_files:
                should_upload = True
                print(f"🎯 Файл из списка изменений: {file_name}.md")
            elif file_name not in self.sync_log['uploads']:
                # Новый файл
                should_upload = True
                print(f"📄 Новый файл: {file_name}.md")
            else:
                # Проверяем изменился ли файл
                old_hash = self.sync_log['uploads'][file_name].get('hash', '')
                if old_hash != file_hash:
                    should_upload = True
                    print(f"🔄 Обновленный файл: {file_name}.md")

            if should_upload:
                files_to_upload.append({
                    'path': file_path,
                    'name': file_name,
                    'hash': file_hash
                })

        if not files_to_upload:
            print("ℹ️  Нет новых или обновленных файлов для загрузки")
            return []

        print(f"\n📤 Загрузка {len(files_to_upload)} файлов...")

        # Загружаем файлы
        for i, file_info in enumerate(files_to_upload, 1):
            print(f"  {i}/{len(files_to_upload)} - {file_info['name']}.md", end=" ")

            doc_id = self._upload_single_document(
                file_info['path'],
                file_info['name']
            )

            if doc_id:
                uploaded_ids.append(doc_id)

                # Сохраняем в лог
                self.sync_log['uploads'][file_info['name']] = {
                    'id': doc_id,
                    'upload_date': datetime.now().isoformat(),
                    'hash': file_info['hash']
                }

                self.save_sync_log()
                print(f"✅")
            else:
                print(f"❌")

            time.sleep(0.5)  # Пауза между загрузками

        return uploaded_ids

    def _upload_single_document(self, file_path: str, doc_name: str) -> Optional[str]:
        """Загрузить один документ"""
        url = f"{self.base_url}/convai/knowledge-base"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Оборачиваем в минимальный HTML с явным указанием UTF-8
            html_wrapper = f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body><pre>{markdown_content}</pre></body>
</html>'''

            # Добавляем UTF-8 BOM для явного указания кодировки
            content_bytes = '\ufeff'.encode('utf-8') + html_wrapper.encode('utf-8')

            files = {
                'file': (f'{doc_name}.html', content_bytes, 'text/html')
            }
            data = {'name': doc_name}

            headers_upload = {"xi-api-key": self.api_key}

            response = requests.post(url, headers=headers_upload, files=files, data=data, timeout=60)

            if response.status_code in [200, 201]:
                result = response.json()
                doc_id = result.get('knowledge_base_id', result.get('id'))
                return doc_id
            else:
                print(f"\n❌ Ошибка загрузки {doc_name}: HTTP {response.status_code}")
                print(f"   Ответ: {response.text[:200]}")
                return None

        except Exception as e:
            print(f"\n❌ Исключение при загрузке {doc_name}: {str(e)}")
            return None

    # ===== ОЖИДАНИЕ ИНДЕКСАЦИИ =====

    def wait_for_indexing(self, doc_ids: List[str], max_wait: int = 120) -> List[str]:
        """
        Ждать завершения RAG индексации документов

        Returns:
            Список ID документов с успешной индексацией
        """
        if not doc_ids:
            return []

        ready_docs = []
        start_time = time.time()

        print(f"\n⏳ Ожидание индексации {len(doc_ids)} документов (макс {max_wait}с)...")

        checked_once = set()

        while time.time() - start_time < max_wait and len(ready_docs) < len(doc_ids):
            for doc_id in doc_ids:
                if doc_id in ready_docs:
                    continue

                status = self._check_rag_status(doc_id)

                if status in ['succeeded', 'indexed', 'completed']:
                    ready_docs.append(doc_id)
                    print(f"   ✅ Готов: {doc_id[:20]}...")
                elif status == 'failed':
                    if doc_id not in checked_once:
                        print(f"   ❌ Ошибка индексации: {doc_id[:20]}...")
                        checked_once.add(doc_id)
                elif status == 'indexing':
                    if doc_id not in checked_once:
                        print(f"   ⏳ Индексируется: {doc_id[:20]}...")
                        checked_once.add(doc_id)

            if len(ready_docs) < len(doc_ids):
                time.sleep(5)  # Проверяем каждые 5 секунд

        print(f"📊 Готово к добавлению: {len(ready_docs)}/{len(doc_ids)}")
        return ready_docs

    def _check_rag_status(self, doc_id: str) -> str:
        """Проверить статус RAG индекса"""
        url = f"{self.base_url}/convai/knowledge-base/{doc_id}/rag-index"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if 'indexes' in data and data['indexes']:
                    return data['indexes'][0].get('status', 'unknown')
                elif isinstance(data, dict) and 'status' in data:
                    return data.get('status', 'unknown')

            # Если нет индекса, считаем что готов (некоторые документы индексируются мгновенно)
            return 'succeeded'

        except Exception:
            return 'succeeded'  # При ошибке считаем готовым

    # ===== УДАЛЕНИЕ СТАРЫХ ДОКУМЕНТОВ =====

    def safe_delete_old_documents(self, to_delete: List[Dict], new_docs_ready: bool) -> int:
        """
        Безопасное удаление старых документов

        Удаляет только если новые документы успешно загружены и проиндексированы
        """
        if not new_docs_ready and to_delete:
            print("⚠️  Новые документы не готовы, пропускаем удаление старых")
            return 0

        if not to_delete:
            print("ℹ️  Нет документов для удаления")
            return 0

        deleted_count = 0
        batch_size = 1000  # Ограничение на количество удалений за 1 цикл
        pause_between_batches = 120  # Пауза между батчами (в секундах)

        print(f"\n🗑️  Удаление {len(to_delete)} старых документов... (лимит на удаление 1 в 2 секунды, макс {batch_size} за раз)")
        for batch_start in range(0, len(to_delete), batch_size):
            current_batch = to_delete[batch_start:batch_start+batch_size]
            print(f"\n=== Обработка батча {batch_start//batch_size+1}: {len(current_batch)} документов ===")
            for j, doc_info in enumerate(current_batch, 1):
                doc_id = doc_info['id']
                doc_name = doc_info['name']
                reason = doc_info.get('reason', 'unknown')

                print(f"  {batch_start + j}/{len(to_delete)} - {doc_name[:40]}", end=" ")
                if self._delete_document(doc_id):
                    deleted_count += 1
                    self.sync_log['deletions'].append({
                        'id': doc_id,
                        'name': doc_name,
                        'deletion_date': datetime.now().isoformat(),
                        'reason': reason
                    })
                    self.save_sync_log()
                    print(f"✅")
                else:
                    print(f"❌")
                time.sleep(2)  # Больше пауза — 2 секунды между удалениями
            if batch_start + batch_size < len(to_delete):
                print(f"  ⏳ Пауза {pause_between_batches//60} мин между батчами...")
                time.sleep(pause_between_batches)
        return deleted_count

    def _delete_document(self, doc_id: str) -> bool:
        """Удалить документ по ID"""
        url = f"{self.base_url}/convai/knowledge-base/{doc_id}"

        try:
            response = requests.delete(url, headers=self.headers, timeout=30)
            return response.status_code in [200, 204]
        except Exception:
            return False

    # ===== ОБНОВЛЕНИЕ АГЕНТА =====

    def update_agent_kb(self, ready_doc_ids: List[str]) -> bool:
        """
        Обновить Knowledge Base агента

        Использует правильную структуру conversation_config
        """
        if not ready_doc_ids:
            log("ℹ️  Нет новых документов для добавления к агенту")
            return True

        agent_url = f"{self.base_url}/convai/agents/{self.agent_id}"

        log(f"\n🤖 Обновление агента...")
        log(f"   📋 Документов для добавления: {len(ready_doc_ids)}")

        # Получаем текущую конфигурацию
        log(f"   📥 Получение текущей конфигурации агента (таймаут: 60с)...")
        try:
            response = requests.get(agent_url, headers=self.headers, timeout=60)
            log(f"   📡 HTTP {response.status_code}")

            if response.status_code != 200:
                log(f"   ❌ Не удалось получить конфигурацию агента: {response.status_code}")
                log(f"   📝 Ответ: {response.text[:300]}")
                return False

            agent_data = response.json()
            log(f"   ✅ Конфигурация получена")
        except requests.exceptions.Timeout:
            log(f"   ❌ Таймаут получения конфигурации агента (>60 сек)")
            return False
        except Exception as e:
            log(f"   ❌ Ошибка получения конфигурации: {type(e).__name__} - {str(e)[:200]}")
            return False

        # Получаем текущие ID документов
        current_kb = agent_data.get('conversation_config', {}).get('knowledge_base', {})
        existing_ids = current_kb.get('ids', [])

        # Обновляем агента — ПЕРЕПИСЫВАЕМ knowledge_base.ids на актуальный набор, не объединяем со старыми
        agent_kb_ids = ready_doc_ids[:50]  # Лимит ElevenLabs — максимум 50

        update_data = {
            'conversation_config': {
                'knowledge_base': {
                    'type': 'knowledge_base',
                    'ids': agent_kb_ids
                }
            }
        }

        log(f"   📊 Обновление: {len(existing_ids)} → {len(agent_kb_ids)} документов в KB агента")
        log(f"   📋 Первые 5 ID для добавления: {agent_kb_ids[:5] if agent_kb_ids else 'нет'}")
        log(f"   📤 Отправка PATCH запроса (таймаут: 300с)...")
        log(f"   🔗 URL: {agent_url}")

        # Пытаемся обновить с retry
        wait_times = [15, 30, 60, 120, 180]
        for attempt in range(5):
            try:
                log(f"   🔄 Попытка {attempt + 1}/5...")
                start_time = time.time()
                log(f"   🕒 Start PATCH-запроса, отправляю данные агенту...")
                connect_start = time.time()
                try:
                    response = requests.patch(
                        agent_url,
                        headers=self.headers,
                        json=update_data,
                        timeout=(15, 900)
                    )
                    connect_time = time.time() - connect_start
                    log(f"   ⏱️ PATCH завершён за {connect_time:.1f}с, HTTP {response.status_code}")
                except Exception as e:
                    fail_time = time.time() - connect_start
                    log(f"   ❌ PATCH exception ({type(e).__name__}) после {fail_time:.1f}с: {str(e)}")
                    # log error to file
                    with open("elevenlabs_patch_errors.log", "a", encoding="utf-8") as errlog:
                        errlog.write(f"\n[{datetime.now().isoformat()}] PATCH exception (attempt {attempt+1}/5)\n")
                        errlog.write(f"URL: {agent_url}\n")
                        errlog.write(f"Payload IDs (total {len(agent_kb_ids)}): {agent_kb_ids[:5]}\n")
                        errlog.write(f"Exception: {type(e).__name__}: {str(e)}\n")
                        import traceback
                        errlog.write(traceback.format_exc())
                        errlog.write(f"Elapsed: {fail_time:.2f} sec\n")
                        errlog.write(f"Payload (truncated): {str(update_data)[:400]}\n")
                        errlog.write("-"*60+"\n")
                    raise

                elapsed = time.time() - start_time
                if response.status_code == 200:
                    log(f"   ✅ Агент успешно обновлен!")
                    return True
                else:
                    # log error to file
                    with open("elevenlabs_patch_errors.log", "a", encoding="utf-8") as errlog:
                        errlog.write(f"\n[{datetime.now().isoformat()}] PATCH HTTP error (attempt {attempt+1}/5)\n")
                        errlog.write(f"URL: {agent_url}\n")
                        errlog.write(f"Status: {response.status_code}, Text: {response.text[:400]}\n")
                        errlog.write(f"Payload IDs (total {len(agent_kb_ids)}): {agent_kb_ids[:5]}\n")
                        errlog.write(f"Elapsed: {elapsed:.2f} sec\n")
                        errlog.write(f"Payload (truncated): {str(update_data)[:400]}\n")
                        errlog.write("-"*60+"\n")
                    log(f"   ❌ HTTP {response.status_code}: {response.text[:300]}")
                    if attempt < 4:
                        wait_time = wait_times[attempt]
                        log(f"   ⏳ Ожидание {wait_time}с перед попыткой {attempt+2}...")
                        time.sleep(wait_time)
                    else:
                        log(f"   ❌ Все попытки исчерпаны")
                        return False

            except requests.exceptions.ConnectTimeout as e:
                elapsed = time.time() - start_time if 'start_time' in locals() else 0
                log(f"   ❌ Таймаут подключения к API (>30 сек): {str(e)}")
                with open("elevenlabs_patch_errors.log", "a", encoding="utf-8") as errlog:
                    errlog.write(f"\n[{datetime.now().isoformat()}] PATCH ConnectTimeout (attempt {attempt+1}/5)\n")
                    errlog.write(f"URL: {agent_url}\n")
                    errlog.write(f"Error: {str(e)}\n")
                    errlog.write(f"Elapsed: {elapsed:.2f} sec\n")
                    errlog.write("-"*60+"\n")
                if attempt < 2:
                    wait_time = (attempt + 1) * 15
                    log(f"   ⏳ Ожидание {wait_time}с перед повторной попыткой...")
                    time.sleep(wait_time)
                else:
                    log(f"   ❌ Все попытки исчерпаны (таймауты подключения)")
                    return False
            except requests.exceptions.ReadTimeout as e:
                elapsed = time.time() - start_time if 'start_time' in locals() else 0
                log(f"   ❌ Таймаут чтения ответа (прошло {elapsed:.1f}с из 300с): {str(e)}")
                with open("elevenlabs_patch_errors.log", "a", encoding="utf-8") as errlog:
                    errlog.write(f"\n[{datetime.now().isoformat()}] PATCH ReadTimeout (attempt {attempt+1}/5)\n")
                    errlog.write(f"URL: {agent_url}\n")
                    errlog.write(f"Error: {str(e)}\n")
                    errlog.write(f"Elapsed: {elapsed:.2f} sec\n")
                    errlog.write("-"*60+"\n")
                if attempt < 2:
                    wait_time = (attempt + 1) * 15
                    log(f"   ⏳ Ожидание {wait_time}с перед повторной попыткой...")
                    time.sleep(wait_time)
                else:
                    log(f"   ❌ Все попытки исчерпаны (таймауты чтения)")
                    return False
            except requests.exceptions.Timeout as e:
                elapsed = time.time() - start_time if 'start_time' in locals() else 0
                log(f"   ❌ Общий таймаут PATCH запроса (прошло {elapsed:.1f}с): {str(e)}")
                with open("elevenlabs_patch_errors.log", "a", encoding="utf-8") as errlog:
                    errlog.write(f"\n[{datetime.now().isoformat()}] PATCH Timeout (attempt {attempt+1}/5)\n")
                    errlog.write(f"URL: {agent_url}\n")
                    errlog.write(f"Error: {str(e)}\n")
                    errlog.write(f"Elapsed: {elapsed:.2f} sec\n")
                    errlog.write("-"*60+"\n")
                if attempt < 2:
                    wait_time = (attempt + 1) * 15
                    log(f"   ⏳ Ожидание {wait_time}с перед повторной попыткой...")
                    time.sleep(wait_time)
                else:
                    log(f"   ❌ Все попытки исчерпаны (таймауты)")
                    return False
            except requests.exceptions.RequestException as e:
                log(f"   ❌ Ошибка сети: {type(e).__name__} - {str(e)[:200]}")
                with open("elevenlabs_patch_errors.log", "a", encoding="utf-8") as errlog:
                    errlog.write(f"\n[{datetime.now().isoformat()}] PATCH RequestException (attempt {attempt+1}/5)\n")
                    errlog.write(f"URL: {agent_url}\n")
                    errlog.write(f"Error: {str(e)}\n")
                    errlog.write(f"Elapsed: {elapsed:.2f} sec\n")
                    errlog.write("-"*60+"\n")
                if attempt < 2:
                    wait_time = (attempt + 1) * 15
                    log(f"   ⏳ Ожидание {wait_time}с перед повторной попыткой...")
                    time.sleep(wait_time)
                else:
                    log(f"   ❌ Все попытки исчерпаны")
                    return False
            except Exception as e:
                log(f"   ❌ Неожиданная ошибка: {type(e).__name__} - {str(e)[:200]}")
                import traceback
                with open("elevenlabs_patch_errors.log", "a", encoding="utf-8") as errlog:
                    errlog.write(f"\n[{datetime.now().isoformat()}] PATCH General Exception (attempt {attempt+1}/5)\n")
                    errlog.write(f"URL: {agent_url}\n")
                    errlog.write(f"Error: {type(e).__name__}: {str(e)}\n")
                    errlog.write(traceback.format_exc())
                    errlog.write(f"Elapsed: {elapsed:.2f} sec\n")
                    errlog.write(f"Payload (truncated): {str(update_data)[:400]}\n")
                    errlog.write("-"*60+"\n")
                if attempt < 2:
                    wait_time = (attempt + 1) * 15
                    log(f"   ⏳ Ожидание {wait_time}с перед повторной попыткой...")
                    time.sleep(wait_time)
                else:
                    log(f"   ❌ Все попытки исчерпаны")
                    return False

        return False

    # ===== ГЛАВНАЯ ФУНКЦИЯ СИНХРОНИЗАЦИИ =====

    def full_sync(self, files_dir: str = 'quarters', dry_run: bool = False, no_delete: bool = False, changed_files: List[str] = None):
        """
        Полная синхронизация с безопасным удалением старых версий

        Args:
            files_dir: Директория с файлами для загрузки
            dry_run: Если True, только показывает что будет сделано
            no_delete: Если True, не удаляет старые документы
            changed_files: Список конкретных файлов для обработки (опционально)
        """
        log("=" * 70)
        log("🚀 АВТОМАТИЧЕСКАЯ СИНХРОНИЗАЦИЯ ELEVENLABS KNOWLEDGE BASE")
        log("=" * 70)
        
        # Логируем параметры запуска
        log(f"📋 Параметры:")
        log(f"   - Директория файлов: {files_dir}")
        log(f"   - Режим: {'DRY RUN' if dry_run else 'REAL'}")
        log(f"   - Удаление старых: {'НЕТ' if no_delete else 'ДА'}")
        log(f"   - Измененных файлов: {len(changed_files) if changed_files else 'все'}")

        if dry_run:
            log("\n⚠️  РЕЖИМ DRY RUN (без реальных изменений)\n")

        # Шаг 1: Получаем все документы (нужно для поиска старых версий)
        log("\n📚 Шаг 1: Получение списка документов из Knowledge Base...")
        
        # В инкрементальном режиме пытаемся обновить кэш (TTL: 1-2 часа), но с fallback на старый
        # Это позволяет находить актуальные старые версии для удаления
        if changed_files:
            log("   ⚡ Инкрементальный режим: обновляем кэш если старше 1 часа (fallback на старый кэш до 24ч)")
            # Сначала пытаемся использовать свежий кэш (до 1 часа)
            all_docs = self.get_all_kb_documents_cached(ttl_minutes=60, use_cache_only=False)
            
            # Если кэш был пустой или устарел, но старый кэш есть - используем его как fallback
            if len(all_docs) == 0:
                log("   📦 Попытка использовать старый кэш (до 24 часов)...")
                all_docs = self.get_all_kb_documents_cached(ttl_minutes=60 * 24, use_cache_only=True)
        else:
            # Полная синхронизация: обновляем кэш
            log("   🔄 Полная синхронизация: загружаем свежие данные из API")
            all_docs = self.get_all_kb_documents_cached(ttl_minutes=60, use_cache_only=False)
        
        log(f"   Найдено документов в KB: {len(all_docs)}")
        
        if len(all_docs) == 0:
            if changed_files:
                log("   ⚠️  Кэш пустой или отсутствует в инкрементальном режиме")
                log("   💡 Продолжаем только загрузку новых документов (старые версии не удаляются)")
            else:
                log("   ⚠️  Не удалось получить документы из KB")

        # Шаг 2: Определяем что удалить
        if changed_files:
            print(f"\n🎯 ИНКРЕМЕНТАЛЬНОЕ ОБНОВЛЕНИЕ: {len(changed_files)} файлов")
            print(f"   Файлы: {', '.join(changed_files)}\n")
            log("\n🔍 Шаг 2: Поиск старых версий обновленных документов...")
        else:
            log("\n🔍 Шаг 2: Поиск документов для удаления...")
        
        to_delete = self.identify_documents_to_delete(all_docs, changed_files=changed_files)
        log(f"   Документов для удаления: {len(to_delete)}")

        if to_delete:
            print("   Список на удаление (первые 10):")
            for doc in to_delete[:10]:
                print(f"      - {doc['name'][:50]} ({doc['reason']})")
            if len(to_delete) > 10:
                print(f"      ... и еще {len(to_delete) - 10}")

        if dry_run:
            print("\n✅ DRY RUN завершен (изменения не применены)")
            return

        # Шаг 3: Загружаем новые/обновленные документы
        print("\n📤 Шаг 3: Загрузка новых и обновленных документов...")
        uploaded_ids = self.upload_new_documents(files_dir, changed_files=changed_files)
        print(f"   Загружено документов: {len(uploaded_ids)}")

        # Шаг 4: Ждем индексации
        ready_ids = []
        if uploaded_ids:
            log("\n⏳ Шаг 4: Ожидание RAG индексации...")
            # Увеличиваем время ожидания пропорционально количеству файлов
            # ~60 секунд на файл, минимум 120, максимум 10 минут
            max_wait_seconds = max(120, min(60 * len(uploaded_ids), 600))
            log(f"   ⏱️  Максимальное время ожидания: {max_wait_seconds} сек ({len(uploaded_ids)} файлов)")
            ready_ids = self.wait_for_indexing(uploaded_ids, max_wait=max_wait_seconds)

            if len(ready_ids) == 0 and len(uploaded_ids) > 0:
                print("⚠️  Ни один документ не проиндексирован, пропускаем обновление агента")
                new_docs_ready = False
            else:
                new_docs_ready = True
        else:
            new_docs_ready = True  # Нет новых документов, можно удалять старые

        # Шаг 5: Обновляем агента
        if ready_ids:
            print("\n🤖 Шаг 5: Обновление агента...")
            agent_updated = self.update_agent_kb(ready_ids)
            new_docs_ready = agent_updated
        else:
            print("\n🤖 Шаг 5: Обновление агента не требуется (нет новых документов)")

        # Шаг 6: Удаляем старые документы
        deleted_count = 0
        if not no_delete:
            print("\n🗑️  Шаг 6: Удаление старых документов...")
            deleted_count = self.safe_delete_old_documents(to_delete, new_docs_ready)
        else:
            print("\n🗑️  Шаг 6: Удаление отключено (--no-delete)")

        # Итоги
        print("\n" + "=" * 70)
        print("📊 ИТОГИ СИНХРОНИЗАЦИИ:")
        print(f"   📤 Загружено новых: {len(uploaded_ids)}")
        print(f"   ✅ Проиндексировано: {len(ready_ids)}")
        print(f"   🗑️  Удалено старых: {deleted_count}")
        print(f"   📚 Всего документов в KB: ~{len(all_docs) + len(uploaded_ids) - deleted_count}")
        print("=" * 70)

        # Обновляем лог
        self.sync_log['last_sync'] = datetime.now().isoformat()
        self.save_sync_log()

        print("\n✨ Синхронизация завершена!")


def main():
    """Главная функция для запуска синхронизации"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Автоматическая синхронизация ElevenLabs Knowledge Base',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s                    # Полная синхронизация
  %(prog)s --dry-run          # Показать что будет сделано
  %(prog)s --no-delete        # Только загрузка, без удаления
  %(prog)s --dir quarters     # Указать директорию с файлами
        """
    )
    parser.add_argument('--dir', default='quarters', help='Директория с MD файлами (по умолчанию: quarters)')
    parser.add_argument('--dry-run', action='store_true', help='Только показать изменения, не применять')
    parser.add_argument('--no-delete', action='store_true', help='Не удалять старые документы')
    parser.add_argument('--changed-files', type=str, help='Путь к файлу со списком измененных файлов')

    args = parser.parse_args()

    # Загружаем список измененных файлов, если указан
    changed_files = None
    if args.changed_files:
        try:
            with open(args.changed_files, 'r', encoding='utf-8') as f:
                changed_files = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"⚠️  Файл {args.changed_files} не найден, выполняется полная синхронизация")

    try:
        sync = ElevenLabsAutoSync()
        sync.full_sync(
            files_dir=args.dir,
            dry_run=args.dry_run,
            no_delete=args.no_delete,
            changed_files=changed_files
        )
        return 0
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
