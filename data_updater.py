#!/usr/bin/env python3
"""
Система автоматического обновления данных BIR.BY
Поддерживает обновление по расписанию и детекцию изменений
"""

import os
import json
import hashlib
import requests
from datetime import datetime, timedelta
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging
from bir_data_parser import BirDataParser

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataUpdater:
    """Система автоматического обновления данных"""
    
    def __init__(self, config_file: str = "update_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.parser = BirDataParser()
        self.data_url = "https://bir.by/ai/json_ai.php"
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Файлы для отслеживания изменений
        self.last_hash_file = self.cache_dir / "last_data_hash.txt"
        self.last_update_file = self.cache_dir / "last_update.json"
        self.stats_file = self.cache_dir / "update_stats.json"
    
    def _load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию обновлений"""
        default_config = {
            "check_interval_minutes": 60,  # Проверка каждый час
            "force_update_hours": 24,      # Принудительное обновление каждые 24 часа
            "enable_change_detection": True,
            "enable_scheduled_updates": True,
            "enable_notifications": True,
            "notification_methods": ["log", "file"],  # log, file, email, webhook
            "webhook_url": None,
            "email_settings": {
                "enabled": False,
                "smtp_server": None,
                "smtp_port": 587,
                "username": None,
                "password": None,
                "to_email": None
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Объединяем с default_config
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logger.error(f"Ошибка загрузки конфигурации: {e}")
                return default_config
        else:
            # Создаем файл конфигурации по умолчанию
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            logger.info(f"Создан файл конфигурации: {self.config_file}")
            return default_config
    
    def _save_config(self):
        """Сохраняет конфигурацию"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _get_data_hash(self, data: Dict[str, Any]) -> str:
        """Вычисляет хеш данных для детекции изменений"""
        # Сортируем данные для стабильного хеша
        sorted_data = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(sorted_data.encode('utf-8')).hexdigest()
    
    def _get_last_hash(self) -> Optional[str]:
        """Получает последний сохраненный хеш данных"""
        if self.last_hash_file.exists():
            try:
                return self.last_hash_file.read_text().strip()
            except Exception as e:
                logger.error(f"Ошибка чтения последнего хеша: {e}")
        return None
    
    def _save_hash(self, hash_value: str):
        """Сохраняет хеш данных"""
        try:
            self.last_hash_file.write_text(hash_value)
        except Exception as e:
            logger.error(f"Ошибка сохранения хеша: {e}")
    
    def _get_last_update_info(self) -> Dict[str, Any]:
        """Получает информацию о последнем обновлении"""
        if self.last_update_file.exists():
            try:
                with open(self.last_update_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка чтения информации об обновлении: {e}")
        return {}
    
    def _save_update_info(self, info: Dict[str, Any]):
        """Сохраняет информацию об обновлении"""
        try:
            with open(self.last_update_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения информации об обновлении: {e}")
    
    def _save_stats(self, stats: Dict[str, Any]):
        """Сохраняет статистику обновлений"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {e}")
    
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Загружает данные с сервера"""
        try:
            logger.info("Загрузка данных с сервера...")
            response = requests.get(self.data_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Успешно загружено {len(data)} объектов")
            return data
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            return None
    
    def check_for_changes(self) -> Tuple[bool, Dict[str, Any]]:
        """Проверяет наличие изменений в данных"""
        data = self.fetch_data()
        if data is None:
            return False, {}
        
        current_hash = self._get_data_hash(data)
        last_hash = self._get_last_hash()
        
        changes_detected = last_hash != current_hash
        
        change_info = {
            'timestamp': datetime.now().isoformat(),
            'data_count': len(data),
            'current_hash': current_hash,
            'last_hash': last_hash,
            'changes_detected': changes_detected
        }
        
        if changes_detected:
            logger.info(f"Обнаружены изменения! Объектов: {len(data)}")
        else:
            logger.info("Изменений не обнаружено")
        
        return changes_detected, change_info
    
    def should_force_update(self) -> bool:
        """Проверяет, нужно ли принудительное обновление"""
        last_update = self._get_last_update_info()
        if not last_update.get('timestamp'):
            return True
        
        last_update_time = datetime.fromisoformat(last_update['timestamp'])
        force_update_interval = timedelta(hours=self.config['force_update_hours'])
        
        return datetime.now() - last_update_time > force_update_interval
    
    def update_data(self, force: bool = False) -> bool:
        """Обновляет данные"""
        try:
            logger.info("🏘️ Начало обновления данных BIR.BY")
            
            # Загружаем и парсим данные
            if not self.parser.fetch_data():
                logger.error("Не удалось загрузить данные")
                return False
            
            # Анализируем проблемные данные
            problematic_count = len([
                item for item in self.parser.data.values()
                if not item.get('Quarter', '').strip()
            ])
            
            # Парсим данные
            self.parser.parse_data()
            
            # Сохраняем новый хеш
            current_hash = self._get_data_hash(self.parser.data)
            self._save_hash(current_hash)
            
            # Сохраняем информацию об обновлении
            update_info = {
                'timestamp': datetime.now().isoformat(),
                'total_objects': len(self.parser.data),
                'quarters_count': len(self.parser.quarters),
                'problematic_objects': problematic_count,
                'force_update': force,
                'hash': current_hash
            }
            self._save_update_info(update_info)
            
            # Сохраняем статистику
            stats = {
                'last_update': update_info,
                'quarters': {
                    name: {
                        'objects_count': sum(len(houses) for houses in quarter.values()),
                        'houses_count': len(quarter)
                    }
                    for name, quarter in self.parser.quarters.items()
                }
            }
            self._save_stats(stats)
            
            logger.info(f"✅ Обновление завершено успешно! Объектов: {len(self.parser.data)}, кварталов: {len(self.parser.quarters)}")
            
            # Отправляем уведомления
            self._send_notifications(update_info)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления данных: {e}")
            return False
    
    def _send_notifications(self, update_info: Dict[str, Any]):
        """Отправляет уведомления об обновлении"""
        if not self.config.get('enable_notifications', True):
            return
        
        methods = self.config.get('notification_methods', ['log'])
        
        message = (
            f"🏘️ BIR.BY данные обновлены!\n"
            f"📊 Объектов: {update_info['total_objects']}\n"
            f"🏢 Кварталов: {update_info['quarters_count']}\n"
            f"⚠️ Проблемных: {update_info['problematic_objects']}\n"
            f"🕐 Время: {update_info['timestamp']}"
        )
        
        if 'log' in methods:
            logger.info(message)
        
        if 'file' in methods:
            notifications_file = self.cache_dir / "notifications.log"
            with open(notifications_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} - {message}\n")
        
        # Здесь можно добавить отправку email, webhook и т.д.
    
    def run_once(self, force: bool = False) -> bool:
        """Выполняет одну проверку и обновление при необходимости"""
        if force:
            logger.info("Принудительное обновление данных...")
            return self.update_data(force=True)
        
        if self.config.get('enable_change_detection', True):
            changes_detected, change_info = self.check_for_changes()
            if changes_detected:
                return self.update_data()
        
        if self.config.get('enable_scheduled_updates', True):
            if self.should_force_update():
                logger.info("Выполняется плановое обновление...")
                return self.update_data(force=True)
        
        return False
    
    def run_daemon(self):
        """Запускает демон для непрерывного мониторинга"""
        logger.info("🚀 Запуск демона автообновления данных BIR.BY")
        logger.info(f"⏰ Интервал проверки: {self.config['check_interval_minutes']} минут")
        logger.info(f"🔄 Принудительное обновление каждые {self.config['force_update_hours']} часов")
        
        while True:
            try:
                self.run_once()
                sleep_time = self.config['check_interval_minutes'] * 60
                logger.debug(f"Ожидание {self.config['check_interval_minutes']} минут до следующей проверки...")
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("Получен сигнал остановки. Завершение работы...")
                break
            except Exception as e:
                logger.error(f"Ошибка в демоне: {e}")
                time.sleep(60)  # Ждем минуту перед повтором
    
    def get_status(self) -> Dict[str, Any]:
        """Получает текущий статус системы обновлений"""
        last_update = self._get_last_update_info()
        last_hash = self._get_last_hash()
        
        status = {
            'config': self.config,
            'last_update': last_update,
            'last_hash': last_hash,
            'cache_dir_exists': self.cache_dir.exists(),
            'next_force_update': None
        }
        
        if last_update.get('timestamp'):
            last_time = datetime.fromisoformat(last_update['timestamp'])
            next_force = last_time + timedelta(hours=self.config['force_update_hours'])
            status['next_force_update'] = next_force.isoformat()
        
        return status


def main():
    """Основная функция CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Система автоматического обновления данных BIR.BY')
    parser.add_argument('--daemon', action='store_true', help='Запустить в режиме демона')
    parser.add_argument('--force', action='store_true', help='Принудительно обновить данные')
    parser.add_argument('--check', action='store_true', help='Проверить изменения без обновления')
    parser.add_argument('--status', action='store_true', help='Показать статус системы')
    parser.add_argument('--config', type=str, default='update_config.json', help='Файл конфигурации')
    
    args = parser.parse_args()
    
    updater = DataUpdater(args.config)
    
    if args.status:
        status = updater.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False, default=str))
        return
    
    if args.check:
        changes_detected, change_info = updater.check_for_changes()
        print(json.dumps(change_info, indent=2, ensure_ascii=False))
        return
    
    if args.force:
        success = updater.update_data(force=True)
        exit(0 if success else 1)
    
    if args.daemon:
        updater.run_daemon()
    else:
        # Выполняем одну проверку
        updater.run_once()


if __name__ == "__main__":
    main()




