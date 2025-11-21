#!/usr/bin/env python3
"""
Website to Knowledge Base Sync
Получение данных с сайта и обновление локальной базы знаний
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class WebsiteDataFetcher:
    """Класс для получения данных с сайта"""
    
    def __init__(self, api_url: str, api_key: str = None):
        self.api_url = api_url
        self.headers = {}
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def fetch_properties(self) -> List[Dict]:
        """Получить список объектов недвижимости с сайта"""
        try:
            response = requests.get(self.api_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных с сайта: {e}")
            return []
    
    def format_property_to_json(self, property_data: Dict) -> Dict:
        """Преобразовать данные объекта в структурированный JSON"""
        # Формируем структурированные данные
        formatted_data = {
            'id': property_data.get('id', 'unknown'),
            'name': property_data.get('name', 'Property'),
            'location': property_data.get('location', ''),
            'developer': property_data.get('developer', ''),
            'completion_date': property_data.get('completion_date', ''),
            'description': property_data.get('description', ''),
            'apartments': [],
            'amenities': property_data.get('amenities', []),
            'payment_options': property_data.get('payment_options', {}),
            'metadata': {
                'updated_at': datetime.now().isoformat(),
                'source': 'website_sync'
            }
        }
        
        # Форматируем информацию о квартирах
        if property_data.get('apartments'):
            for apt in property_data['apartments']:
                apartment = {
                    'type': apt.get('type', 'Apartment'),
                    'area': apt.get('area', 0),
                    'price': apt.get('price', 0),
                    'price_per_sqm': apt.get('price', 0) / apt.get('area', 1) if apt.get('area') else 0,
                    'floor': apt.get('floor', ''),
                    'rooms': apt.get('rooms', 0),
                    'status': apt.get('status', 'available')
                }
                formatted_data['apartments'].append(apartment)
        
        return formatted_data
    
    def save_to_file(self, property_data: Dict, directory: str = "./quarters"):
        """Сохранить данные объекта в JSON файл"""
        # Создаем директорию если не существует
        Path(directory).mkdir(exist_ok=True)
        
        # Генерируем имя файла
        property_id = property_data.get('id', 'unknown')
        property_name = property_data.get('name', 'property').replace(' ', '-').lower()
        filename = f"{str(property_id).zfill(2)}-{property_name}.json"
        filepath = os.path.join(directory, filename)
        
        # Формируем JSON и сохраняем
        json_data = self.format_property_to_json(property_data)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Сохранено: {filename}")
        return filepath


def sync_all_properties():
    """Синхронизировать все объекты с сайта"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_url = os.getenv('WEBSITE_API_URL')
    api_key = os.getenv('WEBSITE_API_KEY')
    
    if not api_url:
        print("❌ Ошибка: Необходимо установить WEBSITE_API_URL в .env")
        return
    
    # Получаем данные с сайта
    fetcher = WebsiteDataFetcher(api_url, api_key)
    properties = fetcher.fetch_properties()
    
    if not properties:
        print("Нет данных для синхронизации")
        return
    
    print(f"📥 Получено {len(properties)} объектов\n")
    
    # Опция 1: Сохраняем как отдельные JSON файлы
    save_as_single_file = os.getenv('SAVE_AS_SINGLE_JSON', 'true').lower() == 'true'
    
    if save_as_single_file:
        # Создаем единый файл базы знаний
        all_properties = []
        for prop in properties:
            json_data = fetcher.format_property_to_json(prop)
            all_properties.append(json_data)
        
        # Создаем единую структуру
        knowledge_base = {
            'version': '1.0',
            'total_properties': len(all_properties),
            'properties': all_properties,
            'metadata': {
                'updated_at': datetime.now().isoformat(),
                'source': 'website_sync'
            }
        }
        
        # Сохраняем в единый файл
        kb_path = './quarters/knowledge-base.json'
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
        
        print(f"✅ База знаний сохранена в {kb_path}")
        print(f"📊 Всего объектов: {len(all_properties)}")
    else:
        # Сохраняем каждый объект отдельно
        updated_files = []
        for prop in properties:
            filepath = fetcher.save_to_file(prop)
            updated_files.append(filepath)
        
        print(f"\n✅ Обновлено {len(updated_files)} файлов")
    
    # Запускаем синхронизацию с ElevenLabs
    if os.getenv('ELEVENLABS_API_KEY') and os.getenv('ELEVENLABS_AGENT_ID'):
        print("\n🔄 Запуск синхронизации с ElevenLabs...")
        os.system('python sync-knowledge-base.py')
    else:
        print("\nℹ️ Для автоматической синхронизации с ElevenLabs ")
        print("установите ELEVENLABS_API_KEY и ELEVENLABS_AGENT_ID")


if __name__ == "__main__":
    sync_all_properties()