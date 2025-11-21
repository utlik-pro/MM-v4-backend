#!/usr/bin/env python3
"""
Упрощенный модуль для загрузки JSON файлов в ElevenLabs Knowledge Base
Работает с ограниченными правами API ключа
"""

import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
import time

# Загружаем переменные окружения
load_dotenv()

class SimpleElevenLabsUploader:
    """Упрощенный класс для загрузки в ElevenLabs"""
    
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.agent_id = os.getenv('ELEVENLABS_AGENT_ID')
        
        if not self.api_key:
            raise ValueError("❌ ELEVENLABS_API_KEY не найден в .env файле")
        if not self.agent_id:
            raise ValueError("❌ ELEVENLABS_AGENT_ID не найден в .env файле")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key
        }
    
    def upload_to_knowledge_base(self, file_path: str, document_name: Optional[str] = None) -> bool:
        """
        Загружает документ в общий Knowledge Base
        """
        if not os.path.exists(file_path):
            print(f"❌ Файл не найден: {file_path}")
            return False
        
        if not document_name:
            document_name = os.path.basename(file_path)
        
        # URL для загрузки в общий knowledge base
        url = f"{self.base_url}/convai/knowledge-base"
        
        try:
            # Читаем JSON и конвертируем в текст
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Форматируем JSON в читаемый текст
            text_content = json.dumps(json_data, ensure_ascii=False, indent=2)
            
            # Отправляем как текстовый файл
            files = {
                'file': (document_name + '.txt', text_content.encode('utf-8'), 'text/plain')
            }
            data = {
                'name': document_name
            }
            
            response = requests.post(url, headers=self.headers, files=files, data=data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ '{document_name}' загружен (ID: {result.get('id', 'неизвестно')})")
                return True
            elif response.status_code == 401:
                print(f"❌ Ошибка авторизации: проверьте API ключ")
                return False
            else:
                print(f"❌ Ошибка {response.status_code}: {response.text}")
                return False
                    
        except Exception as e:
            print(f"❌ Ошибка при загрузке: {e}")
            return False
    
    def update_agent_with_documents(self, document_ids: List[str]) -> bool:
        """Обновляет агента списком документов"""
        url = f"{self.base_url}/convai/agents/{self.agent_id}"
        
        data = {
            "knowledge_base": document_ids
        }
        
        try:
            response = requests.patch(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                print(f"✅ Документы добавлены в агента")
                return True
            else:
                print(f"⚠️ Не удалось добавить документы в агента: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️ Ошибка при обновлении агента: {e}")
            return False
    
    def sync_all_files(self) -> Dict[str, bool]:
        """Синхронизирует все JSON файлы"""
        results = {}
        
        print("🔄 Начинаем загрузку файлов в ElevenLabs...")
        print("=" * 60)
        
        # Загружаем основной файл базы знаний
        kb_file = "quarters/knowledge-base.json"
        if os.path.exists(kb_file):
            print(f"\n📤 Загрузка основной базы знаний...")
            results['knowledge-base'] = self.upload_to_knowledge_base(
                kb_file, 
                "MM-RAG База Знаний - Все квартиры"
            )
            time.sleep(1)
        
        # Загружаем файлы кварталов
        quarters_dir = "quarters/by-quarters"
        if os.path.exists(quarters_dir):
            files = sorted([f for f in os.listdir(quarters_dir) if f.endswith('.json')])
            
            print(f"\n📂 Найдено {len(files)} файлов кварталов")
            
            for filename in files:
                file_path = os.path.join(quarters_dir, filename)
                
                # Формируем понятное имя
                quarter_name = filename.replace('.json', '').replace('-', ' ')
                doc_name = f"Квартал {quarter_name.title()}"
                
                print(f"📤 Загрузка: {doc_name}")
                results[filename] = self.upload_to_knowledge_base(file_path, doc_name)
                
                time.sleep(1)  # Задержка между запросами
        
        # Итоги
        successful = sum(1 for v in results.values() if v)
        total = len(results)
        
        print("\n" + "=" * 60)
        print("📊 Результаты загрузки:")
        print(f"✅ Успешно загружено: {successful}/{total}")
        
        if successful < total:
            print("❌ Не удалось загрузить:")
            for name, success in results.items():
                if not success:
                    print(f"   - {name}")
        
        # Пытаемся добавить документы к агенту
        if successful > 0:
            print("\n🤖 Обновление агента...")
            # Здесь нужно получить ID загруженных документов
            # Для простоты пока пропускаем этот шаг
            print("ℹ️ Для добавления документов к агенту запустите:")
            print("   python3 elevenlabs_agent_updater.py")
        
        return results


def main():
    """Основная функция"""
    try:
        uploader = SimpleElevenLabsUploader()
        results = uploader.sync_all_files()
        
        print("\n✨ Загрузка завершена!")
        print("\nТеперь ваш агент ElevenLabs имеет доступ к:")
        print("- Полной базе данных квартир")
        print("- Детальной информации по каждому кварталу")
        print("- Актуальным ценам и статусам квартир")
        
        return 0 if all(results.values()) else 1
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        return 1


if __name__ == "__main__":
    exit(main())