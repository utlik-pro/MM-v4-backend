#!/usr/bin/env python3
"""
Модуль для загрузки JSON файлов в ElevenLabs Knowledge Base
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
import time

# Загружаем переменные окружения
load_dotenv()

class ElevenLabsUploader:
    """Класс для работы с ElevenLabs API"""
    
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
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Получает информацию об агенте и его Knowledge Base"""
        url = f"{self.base_url}/convai/agents/{self.agent_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка получения информации об агенте: {response.status_code}")
                print(f"   Ответ: {response.text}")
                return {}
        except Exception as e:
            print(f"❌ Ошибка при запросе к ElevenLabs API: {e}")
            return {}
    
    def upload_document(self, file_path: str, document_name: Optional[str] = None) -> bool:
        """
        Загружает документ в Knowledge Base
        
        Args:
            file_path: Путь к файлу для загрузки
            document_name: Имя документа (если не указано, используется имя файла)
        
        Returns:
            True если загрузка успешна, False в противном случае
        """
        if not os.path.exists(file_path):
            print(f"❌ Файл не найден: {file_path}")
            return False
        
        # Определяем имя документа
        if not document_name:
            document_name = os.path.basename(file_path)
        
        # URL для загрузки документа
        url = f"{self.base_url}/convai/agents/{self.agent_id}/knowledge-base/documents"
        
        try:
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Подготавливаем данные для загрузки
            files = {
                'file': (document_name, file_content, 'application/json')
            }
            
            # Убираем Content-Type из заголовков для multipart/form-data
            headers = {
                "xi-api-key": self.api_key
            }
            
            # Отправляем запрос
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code in [200, 201]:
                print(f"✅ Документ '{document_name}' успешно загружен")
                return True
            else:
                print(f"❌ Ошибка загрузки документа: {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при загрузке документа: {e}")
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """Удаляет документ из Knowledge Base"""
        url = f"{self.base_url}/convai/agents/{self.agent_id}/knowledge-base/documents/{document_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code == 200:
                print(f"✅ Документ {document_id} удален")
                return True
            else:
                print(f"❌ Ошибка удаления документа: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при удалении документа: {e}")
            return False
    
    def get_knowledge_base(self):
        """Получает данные Knowledge Base для агента"""
        url = f"{self.base_url}/convai/agents/{self.agent_id}/knowledge-base"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка получения Knowledge Base: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            print(f"❌ Ошибка при получении Knowledge Base: {e}")
            return None

    def list_documents(self) -> List[Dict[str, Any]]:
        """Получает список документов в Knowledge Base"""
        knowledge_base = self.get_knowledge_base()
        if knowledge_base and 'documents' in knowledge_base:
            return knowledge_base['documents']
        return []
    
    def sync_quarters_data(self, quarters_dir: str = "quarters") -> Dict[str, bool]:
        """
        Синхронизирует данные кварталов с ElevenLabs
        
        Args:
            quarters_dir: Директория с JSON файлами кварталов
        
        Returns:
            Словарь с результатами загрузки для каждого файла
        """
        results = {}
        
        # Проверяем наличие директории
        if not os.path.exists(quarters_dir):
            print(f"❌ Директория {quarters_dir} не найдена")
            return results
        
        # Получаем список существующих документов
        existing_docs = self.list_documents()
        existing_names = {doc.get('name', '') for doc in existing_docs}
        
        print(f"📋 Найдено {len(existing_docs)} документов в Knowledge Base")
        
        # Загружаем основной файл knowledge-base.json
        kb_file = os.path.join(quarters_dir, "knowledge-base.json")
        if os.path.exists(kb_file):
            doc_name = "knowledge-base.json"
            print(f"📤 Загрузка {doc_name}...")
            
            # Если документ уже существует, можно его обновить
            if doc_name in existing_names:
                print(f"   ℹ️ Документ уже существует, обновляем...")
            
            success = self.upload_document(kb_file, doc_name)
            results[doc_name] = success
            
            # Небольшая задержка между запросами
            time.sleep(0.5)
        
        # Загружаем файлы кварталов
        for filename in os.listdir(quarters_dir):
            if filename.startswith("quarter-") and filename.endswith(".json"):
                file_path = os.path.join(quarters_dir, filename)
                
                print(f"📤 Загрузка {filename}...")
                
                # Если документ уже существует
                if filename in existing_names:
                    print(f"   ℹ️ Документ уже существует, обновляем...")
                
                success = self.upload_document(file_path, filename)
                results[filename] = success
                
                # Небольшая задержка между запросами
                time.sleep(0.5)
        
        # Выводим итоги
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        print("\n📊 Результаты синхронизации:")
        print(f"   ✅ Успешно загружено: {successful}/{total}")
        
        if successful < total:
            print("   ❌ Не удалось загрузить:")
            for filename, success in results.items():
                if not success:
                    print(f"      - {filename}")
        
        return results


def main():
    """Тестовая функция для проверки загрузки"""
    print("🚀 Запуск загрузки данных в ElevenLabs...")
    print("=" * 60)
    
    try:
        uploader = ElevenLabsUploader()
        
        # Показываем информацию об агенте
        print("\n🤖 Информация об агенте:")
        agent_info = uploader.get_agent_info()
        if agent_info:
            print(f"   Имя: {agent_info.get('name', 'Неизвестно')}")
            print(f"   ID: {uploader.agent_id}")
            kb_docs = agent_info.get('knowledge_base', [])
            print(f"   Документов в KB: {len(kb_docs)}")
        else:
            print("   Не удалось получить информацию об агенте")
        
        # Синхронизируем данные
        print("\n🔄 Начинаем синхронизацию...")
        results = uploader.sync_quarters_data()
        
        print("\n✨ Синхронизация завершена!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())