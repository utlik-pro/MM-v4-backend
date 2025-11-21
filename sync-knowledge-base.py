#!/usr/bin/env python3
"""
ElevenLabs Knowledge Base Sync Script
Автоматическая синхронизация файлов с базой знаний ElevenLabs RAG
"""

import os
import sys
import json
import time
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ElevenLabsKnowledgeSync:
    """Класс для синхронизации базы знаний с ElevenLabs"""
    
    def __init__(self, api_key: str, agent_id: str):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ ElevenLabs
            agent_id: ID агента в ElevenLabs
        """
        self.api_key = api_key
        self.agent_id = agent_id
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        self.knowledge_base_url = f"{self.base_url}/convai/agents/{agent_id}/knowledge-base"
        
    def list_documents(self) -> List[Dict]:
        """Получить список всех документов в базе знаний"""
        try:
            response = requests.get(
                f"{self.knowledge_base_url}/documents",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get('documents', [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении списка документов: {e}")
            return []
    
    def delete_document(self, document_name: str) -> bool:
        """Удалить документ из базы знаний по имени"""
        documents = self.list_documents()
        
        for doc in documents:
            if doc.get('name') == document_name or doc.get('file_name') == document_name:
                doc_id = doc.get('id')
                try:
                    response = requests.delete(
                        f"{self.knowledge_base_url}/documents/{doc_id}",
                        headers=self.headers
                    )
                    response.raise_for_status()
                    print(f"✓ Удален документ: {document_name}")
                    return True
                except requests.exceptions.RequestException as e:
                    print(f"✗ Ошибка удаления {document_name}: {e}")
                    return False
        
        print(f"ℹ Документ {document_name} не найден в базе")
        return True
    
    def upload_document(self, file_path: str, document_name: Optional[str] = None) -> bool:
        """Загрузить документ в базу знаний"""
        if not os.path.exists(file_path):
            print(f"✗ Файл не найден: {file_path}")
            return False
        
        if document_name is None:
            document_name = os.path.basename(file_path)
        
        try:
            # Определяем тип контента по расширению файла
            if file_path.endswith('.json'):
                content_type = 'application/json'
            elif file_path.endswith('.md'):
                content_type = 'text/markdown'
            else:
                content_type = 'text/plain'
            
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Подготавливаем данные для загрузки
            files = {
                'file': (document_name, content, content_type)
            }
            
            # Временно убираем Content-Type для multipart/form-data
            headers = {"xi-api-key": self.api_key}
            
            response = requests.post(
                f"{self.knowledge_base_url}/documents",
                headers=headers,
                files=files,
                data={'name': document_name}
            )
            response.raise_for_status()
            print(f"✓ Загружен документ: {document_name}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Ошибка загрузки {document_name}: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"  Детали: {e.response.text}")
            return False
        except Exception as e:
            print(f"✗ Общая ошибка при загрузке {document_name}: {e}")
            return False
    
    def sync_file(self, file_path: str, force: bool = False) -> bool:
        """
        Синхронизировать один файл
        
        Args:
            file_path: Путь к файлу
            force: Принудительное обновление
        
        Returns:
            True если синхронизация успешна
        """
        file_name = os.path.basename(file_path)
        
        # Проверяем, нужно ли обновление
        if not force and self.is_file_up_to_date(file_path):
            print(f"⏭ Пропуск {file_name} (актуален)")
            return True
        
        print(f"🔄 Синхронизация {file_name}...")
        
        # Удаляем старую версию
        self.delete_document(file_name)
        
        # Небольшая пауза для API
        time.sleep(0.5)
        
        # Загружаем новую версию
        success = self.upload_document(file_path, file_name)
        
        if success:
            self.save_file_hash(file_path)
        
        return success
    
    def sync_directory(self, directory: str, pattern: str = "*.json", force: bool = False):
        """
        Синхронизировать все файлы в директории
        
        Args:
            directory: Путь к директории
            pattern: Паттерн файлов (по умолчанию *.md)
            force: Принудительное обновление всех файлов
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"✗ Директория не найдена: {directory}")
            return
        
        files = sorted(dir_path.glob(pattern))
        
        if not files:
            print(f"✗ Файлы не найдены по паттерну {pattern} в {directory}")
            return
        
        print(f"📁 Найдено {len(files)} файлов для синхронизации\n")
        
        success_count = 0
        for file_path in files:
            if self.sync_file(str(file_path), force):
                success_count += 1
            time.sleep(1)  # Пауза между запросами
        
        print(f"\n✅ Синхронизировано {success_count}/{len(files)} файлов")
    
    def is_file_up_to_date(self, file_path: str) -> bool:
        """Проверить, актуален ли файл (по хешу)"""
        current_hash = self.calculate_file_hash(file_path)
        saved_hash = self.load_file_hash(file_path)
        return current_hash == saved_hash
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Вычислить хеш файла"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def save_file_hash(self, file_path: str):
        """Сохранить хеш файла"""
        hash_file = ".sync_hashes.json"
        hashes = {}
        
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                hashes = json.load(f)
        
        hashes[file_path] = self.calculate_file_hash(file_path)
        
        with open(hash_file, 'w') as f:
            json.dump(hashes, f, indent=2)
    
    def load_file_hash(self, file_path: str) -> Optional[str]:
        """Загрузить сохраненный хеш файла"""
        hash_file = ".sync_hashes.json"
        
        if not os.path.exists(hash_file):
            return None
        
        with open(hash_file, 'r') as f:
            hashes = json.load(f)
        
        return hashes.get(file_path)


def main():
    """
    Основная функция для запуска синхронизации
    
    Использование:
        python sync-knowledge-base.py [--force] [--file <путь>]
    """
    # Загружаем конфигурацию из переменных окружения или .env файла
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('ELEVENLABS_API_KEY')
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')
    
    if not api_key or not agent_id:
        print("❌ Ошибка: Необходимо установить ELEVENLABS_API_KEY и ELEVENLABS_AGENT_ID")
        print("\nДобавьте в файл .env:")
        print("ELEVENLABS_API_KEY=your_api_key")
        print("ELEVENLABS_AGENT_ID=your_agent_id")
        sys.exit(1)
    
    # Парсим аргументы
    force = '--force' in sys.argv
    
    # Создаем клиент
    sync = ElevenLabsKnowledgeSync(api_key, agent_id)
    
    # Проверяем, указан ли конкретный файл
    if '--file' in sys.argv:
        file_index = sys.argv.index('--file') + 1
        if file_index < len(sys.argv):
            file_path = sys.argv[file_index]
            print(f"🔄 Синхронизация файла: {file_path}\n")
            sync.sync_file(file_path, force)
        else:
            print("❌ Ошибка: После --file должен быть указан путь к файлу")
    else:
        # Синхронизируем JSON файлы в директории quarters
        print("🚀 Запуск синхронизации базы знаний MM-RAG\n")
        
        # Проверяем наличие JSON файлов
        json_pattern = '*.json'
        md_pattern = '*.md'
        
        # Если есть knowledge-base.json, синхронизируем его
        if os.path.exists('./quarters/knowledge-base.json'):
            print("📋 Обнаружен единый файл базы знаний")
            sync.sync_file('./quarters/knowledge-base.json', force)
        else:
            # Иначе синхронизируем отдельные JSON файлы
            sync.sync_directory('./quarters', json_pattern, force)


if __name__ == "__main__":
    main()