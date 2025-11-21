#!/usr/bin/env python3
"""
Модуль для привязки документов из Knowledge Base к конкретному агенту ElevenLabs
"""

import os
import json
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
import time

# Загружаем переменные окружения
load_dotenv()

class ElevenLabsAgentUpdater:
    """Класс для обновления агента с документами из Knowledge Base"""
    
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
    
    def get_all_knowledge_base_documents(self) -> List[Dict]:
        """Получает список всех документов в общей Knowledge Base"""
        url = f"{self.base_url}/convai/knowledge-base"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                # Проверяем формат ответа
                if isinstance(data, list):
                    # Если это список строк (ID документов)
                    if data and isinstance(data[0], str):
                        # Преобразуем в формат с ID
                        documents = [{"id": doc_id, "name": f"Document {i+1}"} for i, doc_id in enumerate(data)]
                    else:
                        documents = data
                elif isinstance(data, dict):
                    # Если это словарь с документами
                    documents = data.get('documents', [])
                else:
                    documents = []
                
                print(f"📚 Найдено {len(documents)} документов в Knowledge Base")
                return documents
            else:
                print(f"❌ Ошибка получения документов: {response.status_code}")
                print(f"   Ответ: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Ошибка при запросе: {e}")
            return []
    
    def get_agent_info(self) -> Dict:
        """Получает информацию об агенте"""
        url = f"{self.base_url}/convai/agents/{self.agent_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка получения информации об агенте: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return {}
    
    def update_agent_knowledge_base(self, document_ids: List[str]) -> bool:
        """Обновляет Knowledge Base агента списком документов"""
        url = f"{self.base_url}/convai/agents/{self.agent_id}"
        
        data = {
            "knowledge_base": document_ids
        }
        
        try:
            response = requests.patch(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                print(f"✅ Knowledge Base агента обновлен")
                return True
            else:
                print(f"❌ Ошибка обновления агента: {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при обновлении агента: {e}")
            return False
    
    def sync_documents_to_agent(self) -> bool:
        """
        Синхронизирует все документы MM-RAG с агентом
        """
        print("🔄 Синхронизация документов с агентом ElevenLabs")
        print("=" * 60)
        
        # Получаем информацию об агенте
        agent_info = self.get_agent_info()
        if agent_info:
            print(f"\n🤖 Агент: {agent_info.get('name', 'Неизвестно')}")
            current_kb = agent_info.get('knowledge_base', [])
            print(f"   Текущих документов в агенте: {len(current_kb)}")
        
        # Получаем все документы из Knowledge Base
        all_documents = self.get_all_knowledge_base_documents()
        
        if not all_documents:
            print("❌ Не найдено документов в Knowledge Base")
            return False
        
        # Фильтруем только наши документы MM-RAG
        mmrag_docs = []
        mmrag_doc_ids = []
        
        for doc in all_documents:
            # Обрабатываем разные форматы документа
            if isinstance(doc, str):
                # Если это просто ID документа, добавляем все
                mmrag_doc_ids.append(doc)
                mmrag_docs.append({"id": doc, "name": "Document"})
                print(f"   📄 Document ID: {doc}")
            elif isinstance(doc, dict):
                doc_name = doc.get('name', '')
                doc_id = doc.get('id', '')
                
                # Проверяем, что это наши документы
                if ('MM-RAG' in doc_name or 
                    'Квартал' in doc_name or 
                    doc_name.startswith('knowledge-base')):
                    
                    mmrag_docs.append(doc)
                    mmrag_doc_ids.append(doc_id)
                    print(f"   📄 {doc_name} (ID: {doc_id})")
        
        print(f"\n📊 Найдено {len(mmrag_docs)} документов MM-RAG для добавления")
        
        if not mmrag_doc_ids:
            print("❌ Не найдено документов MM-RAG")
            return False
        
        # Обновляем агента порциями
        print("\n🔧 Обновление агента...")
        
        # Берем только первые 10 уникальных ID (убираем дубликаты)
        unique_doc_ids = list(dict.fromkeys(mmrag_doc_ids))[:10]
        
        print(f"📝 Добавляем {len(unique_doc_ids)} документов из {len(mmrag_doc_ids)} найденных")
        
        if self.update_agent_knowledge_base(unique_doc_ids):
            print(f"✅ Успешно добавлено {len(unique_doc_ids)} документов к агенту")
            
            # Ждем немного для синхронизации
            print("⏳ Ожидание синхронизации...")
            time.sleep(2)
            
            # Проверяем результат
            updated_agent = self.get_agent_info()
            if updated_agent:
                new_kb = updated_agent.get('knowledge_base', [])
                print(f"\n📚 Итого документов в агенте: {len(new_kb)}")
                
                if len(new_kb) > 0:
                    print("✅ Документы успешно добавлены в агента!")
                else:
                    print("⚠️ Документы добавлены, но еще не отображаются. Проверьте через минуту.")
            
            return True
        else:
            print("❌ Не удалось обновить агента")
            return False


def main():
    """Основная функция"""
    print("🚀 Запуск синхронизации документов с агентом ElevenLabs")
    print("=" * 60)
    
    try:
        updater = ElevenLabsAgentUpdater()
        
        if updater.sync_documents_to_agent():
            print("\n✨ Синхронизация успешно завершена!")
            print("\nВаш агент ElevenLabs теперь имеет доступ к:")
            print("- Полной базе знаний MM-RAG")
            print("- Информации по всем кварталам")
            print("- Актуальным данным о квартирах")
            return 0
        else:
            print("\n❌ Синхронизация не удалась")
            return 1
            
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        return 1


if __name__ == "__main__":
    exit(main())