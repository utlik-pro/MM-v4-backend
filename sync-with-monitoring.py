#!/usr/bin/env python3
"""
Мониторинг изменений и синхронизация с bir.by
Автоматически проверяет изменения и обновляет базу знаний
"""

import os
import sys
import re
import json
import requests
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
# from deepdiff import DeepDiff  # Опционально
import schedule


class PropertyMonitor:
    """Класс для мониторинга изменений в данных недвижимости"""
    
    def __init__(self, source_url: str = "https://bir.by/ai/json_ai.php"):
        self.source_url = source_url
        self.data_dir = Path('./quarters')
        self.history_file = self.data_dir / 'version-history.json'
        self.current_data_file = self.data_dir / 'knowledge-base.json'
        self.quarters_dir = self.data_dir / 'by-quarters'
        self.quarter_hashes_file = self.data_dir / '.quarter_hashes.json'
        self.data_dir.mkdir(exist_ok=True)
        self.quarters_dir.mkdir(exist_ok=True)

        # Загружаем историю версий
        self.version_history = self.load_version_history()

        # Список измененных файлов (для передачи в ElevenLabs sync)
        self.changed_md_files = []
    
    def load_version_history(self) -> List[Dict]:
        """Загрузить историю версий из файла"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_version_history(self):
        """Сохранить историю версий в файл"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.version_history, f, ensure_ascii=False, indent=2)

    def load_quarter_hashes(self) -> Dict[str, str]:
        """Загрузить хеши кварталов из файла"""
        if self.quarter_hashes_file.exists():
            with open(self.quarter_hashes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_quarter_hashes(self, hashes: Dict[str, str]):
        """Сохранить хеши кварталов в файл"""
        with open(self.quarter_hashes_file, 'w', encoding='utf-8') as f:
            json.dump(hashes, f, ensure_ascii=False, indent=2)

    def generate_quarter_markdown(self, quarter_data: Dict) -> str:
        """
        Генерация markdown контента из данных квартала

        Args:
            quarter_data: Словарь с данными квартала (apartments, statistics, quarter)

        Returns:
            Строка с markdown контентом
        """
        quarter_name = quarter_data.get('quarter', 'Unknown')
        apartments = quarter_data.get('apartments', [])
        stats = quarter_data.get('statistics', {})

        # Заголовок
        md = f"# 🏘️ Квартал — {quarter_name}\n\n"
        md += f"## 📍 Общая информация\n\n"
        md += f"**Квартал:** {quarter_name}\n"
        md += f"**Город:** Минск\n"
        md += f"**Район:** Мир\n"
        md += f"**Количество объектов:** {len(apartments)}\n"
        md += f"**Тип недвижимости:** Квартира\n\n"

        # Статистика
        md += f"## 📊 Статистика\n\n"
        md += f"**Диапазон площадей:** {stats.get('min_area', 0):.1f} - {stats.get('max_area', 0):.1f} м²\n"
        md += f"**Средняя цена за м²:** {int(stats.get('avg_price_per_m2', 0))} евро\n"
        md += f"**Общая стоимость:** {int(stats.get('min_total_price', 0)):,} - {int(stats.get('max_total_price', 0)):,} евро\n\n"

        # Группировка по домам
        houses = {}
        for apt in apartments:
            house_num = apt.get('house_number', 'Unknown')
            if house_num not in houses:
                houses[house_num] = []
            houses[house_num].append(apt)

        # Документирование каждого дома
        for house_num in sorted(houses.keys()):
            house_apartments = houses[house_num]
            if not house_apartments:
                continue

            first_apt = house_apartments[0]
            house_name = first_apt.get('house_name', 'N/A')

            md += f"## 🏠 Дом {house_num}\n\n"
            md += f"**Название дома:** {house_name}\n\n"
            md += f"### 📊 Статистика дома\n"
            md += f"**Количество апартаментов:** {len(house_apartments)}\n"

            # Диапазон площадей дома
            areas = [apt['area'] for apt in house_apartments if 'area' in apt]
            if areas:
                md += f"**Диапазон площадей:** {min(areas):.1f} - {max(areas):.1f} м²\n"

            # Средние цены дома
            prices = [apt['price_per_m2'] for apt in house_apartments if 'price_per_m2' in apt and apt['price_per_m2'] > 0]
            if prices:
                md += f"**Средняя цена за м²:** {int(sum(prices) / len(prices))} евро\n"

            total_prices = [apt['total_price'] for apt in house_apartments if 'total_price' in apt and apt['total_price'] > 0]
            if total_prices:
                md += f"**Средняя стоимость:** {int(sum(total_prices) / len(total_prices)):,} евро\n"

            md += "\n\n"

            # Группировка по этажам
            floors = {}
            for apt in house_apartments:
                floor = apt.get('floor', 0)
                if floor not in floors:
                    floors[floor] = []
                floors[floor].append(apt)

            # Документирование каждого этажа
            for floor_num in sorted(floors.keys()):
                if floor_num == 0:
                    continue

                md += f"## 🏢 Этаж {floor_num}\n\n"

                floor_apartments = sorted(floors[floor_num],
                                         key=lambda x: (x.get('rooms', 0), x.get('apartment', '')))

                for apt in floor_apartments:
                    md += f"### 🏠 Квартира {apt.get('apartment', 'N/A')}\n\n"
                    md += f"**Квартал:** {quarter_name}\n"
                    md += f"**Дом:** {house_num}\n"
                    md += f"**Название дома:** {house_name}\n"
                    md += f"**Этаж:** {floor_num}\n"
                    md += f"**Этажность дома:** {apt.get('total_floors', 'N/A')}\n"
                    md += f"**Количество комнат:** {apt.get('rooms', 'N/A')}\n"
                    md += f"**Площадь:** {apt.get('area', 'N/A')} м²\n"
                    md += f"**Цена за м²:** {apt.get('price_per_m2', 'N/A')} евро\n"
                    md += f"**Общая стоимость:** {apt.get('total_price', 'N/A'):,} евро\n" if isinstance(apt.get('total_price'), (int, float)) else f"**Общая стоимость:** {apt.get('total_price', 'N/A')}\n"
                    md += f"**Статус:** {apt.get('status', 'N/A')}\n"
                    md += f"**Адрес:** {apt.get('address', 'N/A')}\n"
                    md += f"**Местоположение:** {apt.get('location', 'N/A')}\n"
                    md += "\n\n---\n\n"

        return md

    def convert_quarters_json_to_md(self) -> List[str]:
        """
        Конвертировать JSON файлы кварталов в MD формат для ElevenLabs

        Returns:
            Список сгенерированных MD файлов
        """
        md_files = []

        if not self.quarters_dir.exists():
            print(f"❌ Директория не найдена: {self.quarters_dir}")
            return md_files

        for json_file in self.quarters_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Генерируем markdown из JSON
                md_content = self.generate_quarter_markdown(data)

                # Создаем имя MD файла из имени квартала
                quarter_name = data.get('quarter', json_file.stem)
                # Транслитерация и очистка имени файла
                md_name = self._transliterate_quarter_name(quarter_name)
                md_path = self.data_dir / f"{md_name}.md"

                # Сохраняем MD файл
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                md_files.append(f"{md_name}.md")
                print(f"  📝 Сгенерирован: {md_name}.md")

            except Exception as e:
                print(f"  ❌ Ошибка конвертации {json_file.name}: {e}")

        return md_files

    def _transliterate_quarter_name(self, quarter_name: str) -> str:
        """
        Транслитерация названия квартала для имени файла

        Args:
            quarter_name: Название квартала (например "29 Северная Европа")

        Returns:
            Транслитерированное имя файла (например "29-severnaya-evropa")
        """
        # Таблица транслитерации
        translit_table = {
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }

        # Транслитерация
        result = ''
        for char in quarter_name:
            if char in translit_table:
                result += translit_table[char]
            elif char.isalnum() or char.isspace() or char == '-':
                result += char
            else:
                result += '-'

        # Очистка и форматирование
        result = result.replace(' ', '-')
        result = re.sub(r'-+', '-', result)  # Удаление повторяющихся дефисов
        result = result.strip('-')  # Удаление дефисов в начале и конце
        # НЕ конвертируем в lowercase - сохраняем регистр

        return result

    def fetch_current_data(self) -> Optional[Dict]:
        """Получить текущие данные с сайта"""
        try:
            print(f"📥 Получение данных с {self.source_url}...")
            response = requests.get(self.source_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при получении данных: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка декодирования JSON: {e}")
            return None
    
    def calculate_hash(self, data: Dict) -> str:
        """Вычислить хеш данных для определения изменений"""
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def load_current_knowledge_base(self) -> Optional[Dict]:
        """Загрузить текущую базу знаний"""
        if self.current_data_file.exists():
            with open(self.current_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def detect_changes(self, old_data: Dict, new_data: Dict) -> Dict:
        """Определить конкретные изменения между версиями"""
        changes = {
            'timestamp': datetime.now().isoformat(),
            'summary': [],
            'details': {}
        }
        
        # Простое сравнение без DeepDiff
        old_props = {p.get('id'): p for p in old_data.get('properties', [])}
        new_props = {p.get('id'): p for p in new_data.get('properties', [])}
        
        # Находим добавленные объекты
        added = set(new_props.keys()) - set(old_props.keys())
        if added:
            changes['summary'].append(f"Добавлено объектов: {len(added)}")
            changes['details']['added'] = list(added)
        
        # Находим удаленные объекты
        removed = set(old_props.keys()) - set(new_props.keys())
        if removed:
            changes['summary'].append(f"Удалено объектов: {len(removed)}")
            changes['details']['removed'] = list(removed)
        
        # Проверяем изменения в существующих объектах
        for prop_id in set(old_props.keys()) & set(new_props.keys()):
            old_prop = old_props[prop_id]
            new_prop = new_props[prop_id]
            
            # Сравниваем квартиры
            old_apts = {a.get('number'): a for a in old_prop.get('apartments', [])}
            new_apts = {a.get('number'): a for a in new_prop.get('apartments', [])}
            
            for apt_num in set(old_apts.keys()) & set(new_apts.keys()):
                old_apt = old_apts[apt_num]
                new_apt = new_apts[apt_num]
                
                # Проверяем статус
                if old_apt.get('status') != new_apt.get('status'):
                    changes['summary'].append(
                        f"Квартира {apt_num}: статус изменен с '{old_apt.get('status')}' на '{new_apt.get('status')}'"
                    )
                
                # Проверяем цену
                if old_apt.get('price') != new_apt.get('price'):
                    changes['summary'].append(
                        f"Квартира {apt_num}: цена изменена с {old_apt.get('price')} на {new_apt.get('price')}"
                    )
        
        return changes
    
    def extract_number(self, value: Any) -> float:
        """Извлечь число из значения"""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Удаляем все нечисловые символы кроме точки и запятой
            numbers = re.findall(r'[\d.,]+', value)
            if numbers:
                # Берем первое найденное число
                num_str = numbers[0].replace(',', '.')
                try:
                    return float(num_str)
                except ValueError:
                    return 0
        return 0
    
    def extract_quarter_name(self, quarter_str: str) -> str:
        """Извлечь название квартала из строки"""
        # Пример: "Квартал — 29 Северная Европа" -> "29-Северная-Европа"
        if '—' in quarter_str:
            parts = quarter_str.split('—')[1].strip()
        elif '-' in quarter_str:
            parts = quarter_str.split('-', 1)[1].strip() if quarter_str.startswith('Квартал') else quarter_str
        else:
            parts = quarter_str.replace('Квартал', '').strip()
        
        # Очищаем и форматируем название
        clean_name = parts.replace(' ', '-').replace('/', '-').replace('\\', '-')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c in '-_')
        return clean_name or 'unknown-quarter'
    
    def split_data_by_quarters(self, data: Dict) -> Dict[str, List]:
        """Разделить данные по кварталам"""
        quarters_data = {}
        
        # Если данные уже структурированы по properties
        if 'properties' in data:
            for prop in data['properties']:
                quarter_name = prop.get('quarter', 'unknown')
                if quarter_name not in quarters_data:
                    quarters_data[quarter_name] = []
                quarters_data[quarter_name].append(prop)
        else:
            # Если это сырые данные с bir.by
            for apt_id, apt_data in data.items():
                if isinstance(apt_data, dict):
                    # Пытаемся получить квартал из поля Quarter
                    quarter_str = apt_data.get('Quarter', '')
                    
                    # Если Quarter отсутствует, пытаемся определить по Location или NumberHouse
                    if not quarter_str:
                        location = apt_data.get('Location', '')
                        number_house = apt_data.get('NumberHouse', '')
                        
                        # Проверяем специальные случаи для квартала 02 Эмиратс
                        # Дома: Эмиратс Волна, Жемчужина 2, Марина 1, Диадема
                        house_name = apt_data.get('NameHouse', '').lower()
                        number_house_lower = number_house.lower()
                        location_lower = location.lower()
                        
                        # СНАЧАЛА проверяем квартал 18 для Сидней Люкс 18.4 и Рио-де-Жанейро 18.7
                        if 'сидней люкс 18.4' in number_house_lower or 'сидней люкс 18.4' in house_name.lower():
                            quarter_str = 'Квартал — 18 Чемпионов'
                        elif 'рио-де-жанейро 18.7' in number_house_lower or 'рио-де-жанейро 18.7' in house_name.lower():
                            quarter_str = 'Квартал — 18 Чемпионов'
                        else:
                            # Квартал 02 Эмиратс включает:
                            # - Эмиратс Волна (любые)
                            # - Жемчужина 2
                            # - Марина 1
                            # - Диадема (любые)
                            is_emirates = False
                            
                            if 'эмиратс' in location_lower or 'эмиратс' in number_house_lower:
                                is_emirates = True
                            elif 'жемчужина 2' in number_house_lower:
                                is_emirates = True
                            elif 'марина 1' in number_house_lower:
                                is_emirates = True
                            elif 'диадема' in number_house_lower.lower() or house_name == 'диадема':
                                is_emirates = True  # Диадема всегда относится к квартал 02
                            
                            if is_emirates:
                                quarter_str = 'Квартал — 02 Эмиратс'
                            else:
                                # Пытаемся извлечь из Location (например: "Минск Мир, Дом 21.6")
                                import re
                                match = re.search(r'Дом\s+(\d+)', location)
                                if match:
                                    quarter_num = match.group(1).split('.')[0]
                                    quarter_str = f'Квартал — {quarter_num}'
                                else:
                                    # Проверяем NumberHouse на наличие номера квартала
                                    match = re.search(r'^(\d+)', number_house)
                                    if match:
                                        quarter_num = match.group(1)
                                        quarter_str = f'Квартал — {quarter_num}'
                                    else:
                                        quarter_str = 'Квартал — Неизвестный'
                    
                    if quarter_str:
                        quarter_name = self.extract_quarter_name(quarter_str)
                    
                    if quarter_name not in quarters_data:
                        quarters_data[quarter_name] = []
                    
                    # Проверяем тип объекта - пропускаем машиноместа
                    apt_type = apt_data.get('type', 'Квартира')
                    if 'машиноместо' in apt_type.lower():
                        continue  # Пропускаем машиноместа
                    
                    # Обработка и исправление поля FloorTotal
                    floor_total_raw = apt_data.get('FloorTotal', '')
                    floor_total = floor_total_raw
                    
                    # Исправляем известные проблемы с этажностью
                    if floor_total == 'Этажность дома: 2.4':
                        floor_total = 'Этажность дома: 24'
                    elif floor_total == 'Этажность дома: 2.5':
                        floor_total = 'Этажность дома: 25'
                    elif floor_total == 'Этажность дома: ':
                        # Для домов Эмиратс Волна и Жемчужина устанавливаем 22 этажа
                        number_house = apt_data.get('NumberHouse', '').lower()
                        if 'эмиратс волна' in number_house or 'жемчужина' in number_house:
                            floor_total = 'Этажность дома: 22'
                        else:
                            floor_total = 'Этажность дома: не указано'
                    
                    # Форматируем данные квартиры
                    formatted_apt = {
                        'id': apt_id,
                        'apartment': apt_data.get('Apartment', ''),
                        'type': apt_type,
                        'quarter': quarter_str,
                        'status': apt_data.get('Status', ''),
                        'address': apt_data.get('Address', ''),
                        'location': apt_data.get('Location', ''),
                        'house_number': apt_data.get('NumberHouse', ''),
                        'house_name': apt_data.get('NameHouse', ''),
                        'floor': apt_data.get('Floor', ''),
                        'floor_total': floor_total,
                        'area': self.extract_number(apt_data.get('Square', 0)),
                        'price_per_sqm': self.extract_number(apt_data.get('Price_metr', 0)),
                        'total_price': self.extract_number(apt_data.get('Price_full', 0))
                    }
                    quarters_data[quarter_name].append(formatted_apt)
        
        return quarters_data
    
    def save_quarters_data(self, quarters_data: Dict[str, List]):
        """Сохранить данные каждого квартала в отдельный JSON файл (только измененные)"""
        saved_files = []
        changed_files = []

        # Загружаем предыдущие хеши кварталов
        quarter_hashes = self.load_quarter_hashes()
        new_hashes = {}

        for quarter_name, apartments in quarters_data.items():
            # Формируем структуру файла квартала
            quarter_data = {
                'version': '1.0',
                'quarter': quarter_name,
                'updated_at': datetime.now().isoformat(),
                'total_apartments': len(apartments),
                'apartments': apartments,
                'statistics': {
                    'min_price': min((a['total_price'] for a in apartments if a['total_price'] > 0), default=0),
                    'max_price': max((a['total_price'] for a in apartments if a['total_price'] > 0), default=0),
                    'avg_price': sum(a['total_price'] for a in apartments) / len(apartments) if apartments else 0,
                    'min_area': min((a['area'] for a in apartments if a['area'] > 0), default=0),
                    'max_area': max((a['area'] for a in apartments if a['area'] > 0), default=0),
                    'available_count': len([a for a in apartments if 'Сдано' not in a.get('status', '') and 'Бронь' not in a.get('status', '')])
                }
            }

            # Вычисляем хеш данных квартала (без updated_at для корректного сравнения)
            data_for_hash = {
                'apartments': apartments,
                'statistics': quarter_data['statistics']
            }
            quarter_hash = hashlib.sha256(
                json.dumps(data_for_hash, sort_keys=True, ensure_ascii=False).encode('utf-8')
            ).hexdigest()

            # Сохраняем новый хеш
            new_hashes[quarter_name] = quarter_hash

            # Проверяем, изменился ли квартал
            if quarter_hashes.get(quarter_name) == quarter_hash:
                # Квартал не изменился, пропускаем сохранение
                print(f"  ⏭️  Квартал {quarter_name}: без изменений ({len(apartments)} квартир)")
                continue

            # Квартал изменился или новый, сохраняем
            file_path = self.quarters_dir / f"{quarter_name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(quarter_data, f, ensure_ascii=False, indent=2)

            saved_files.append(str(file_path))
            changed_files.append(quarter_name)

            # Показываем статус
            if quarter_name in quarter_hashes:
                print(f"  ✏️  Квартал {quarter_name}: обновлен ({len(apartments)} квартир)")
            else:
                print(f"  ➕ Квартал {quarter_name}: новый ({len(apartments)} квартир)")

        # Сохраняем обновленные хеши
        self.save_quarter_hashes(new_hashes)

        # НЕ сохраняем список здесь - будет создан в convert_quarters_json_to_md()

        if changed_files:
            print(f"\n📝 Изменено кварталов: {len(changed_files)} из {len(quarters_data)}")
        else:
            print(f"\n✅ Все {len(quarters_data)} кварталов актуальны, изменений нет")

        return saved_files
    
    def process_data(self, raw_data: Any) -> Dict:
        """Обработать сырые данные в структурированный формат"""
        # Если данные уже в нужном формате
        if isinstance(raw_data, dict) and 'properties' in raw_data:
            return raw_data
        
        # Если это массив объектов недвижимости
        if isinstance(raw_data, list):
            processed_properties = []
            
            for item in raw_data:
                property_data = {
                    'id': item.get('id', ''),
                    'name': item.get('name', ''),
                    'quarter': item.get('quarter', ''),
                    'city': item.get('city', ''),
                    'address': item.get('address', ''),
                    'building': item.get('building', ''),
                    'apartments': []
                }
                
                # Обрабатываем квартиры
                if 'apartments' in item:
                    for apt in item['apartments']:
                        apartment = {
                            'number': apt.get('number', ''),
                            'area': apt.get('area', 0),
                            'floor': apt.get('floor', 0),
                            'price': apt.get('price', 0),
                            'price_per_sqm': apt.get('price_per_sqm', 0),
                            'status': apt.get('status', 'available'),
                            'rooms': apt.get('rooms', 0)
                        }
                        property_data['apartments'].append(apartment)
                
                processed_properties.append(property_data)
            
            return {
                'version': '1.0',
                'source': self.source_url,
                'updated_at': datetime.now().isoformat(),
                'total_properties': len(processed_properties),
                'properties': processed_properties
            }
        
        # Если формат неизвестен, возвращаем как есть
        return {
            'version': '1.0',
            'source': self.source_url,
            'updated_at': datetime.now().isoformat(),
            'data': raw_data
        }
    
    def check_and_update(self) -> bool:
        """Проверить изменения и обновить базу знаний при необходимости"""
        print(f"\n{'='*60}")
        print(f"🕐 Проверка изменений: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Получаем новые данные
        new_raw_data = self.fetch_current_data()
        if not new_raw_data:
            print("⚠️ Не удалось получить данные")
            return False
        
        # Обрабатываем данные
        new_data = self.process_data(new_raw_data)
        new_hash = self.calculate_hash(new_data)
        
        # Загружаем текущую базу знаний
        current_data = self.load_current_knowledge_base()
        
        # Проверяем, есть ли изменения
        if current_data:
            current_hash = self.calculate_hash(current_data)
            
            if current_hash == new_hash:
                print("✅ Изменений не обнаружено")
                return False
            
            # Есть изменения - анализируем их
            print("🔄 Обнаружены изменения!")
            changes = self.detect_changes(current_data, new_data)
            
            # Выводим сводку изменений
            if changes['summary']:
                print("\n📊 Сводка изменений:")
                for summary in changes['summary']:
                    print(f"  • {summary}")
        else:
            print("📝 Первичная загрузка данных")
            changes = {
                'timestamp': datetime.now().isoformat(),
                'summary': ['Первичная загрузка базы данных'],
                'details': {'initial_load': True}
            }
        
        # Сохраняем новую версию
        with open(self.current_data_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        print(f"💾 База знаний обновлена: {self.current_data_file}")
        
        # Разделяем данные по кварталам
        print("\n📂 Сохранение данных по кварталам:")
        quarters_data = self.split_data_by_quarters(new_data.get('data', new_data))
        self.save_quarters_data(quarters_data)

        # Генерируем MD файлы из JSON для ElevenLabs
        print("\n📄 Генерирование MD файлов из JSON:")
        md_files = self.convert_quarters_json_to_md()
        if md_files:
            self.changed_md_files.extend(md_files)
            print(f"✅ Сгенерировано MD файлов: {len(md_files)}")

        # Добавляем запись в историю версий
        version_entry = {
            'version': len(self.version_history) + 1,
            'timestamp': datetime.now().isoformat(),
            'hash': new_hash,
            'changes': changes,
            'total_properties': new_data.get('total_properties', 0),
            'total_apartments': sum(
                len(prop.get('apartments', []))
                for prop in new_data.get('properties', [])
            )
        }
        
        self.version_history.append(version_entry)
        self.save_version_history()
        print(f"📜 История версий обновлена (версия {version_entry['version']})")
        
        # Синхронизация с ElevenLabs отключена (данные только локально)
        print("\nℹ️ Данные обновлены локально в quarters/")
        print("   Для загрузки в ElevenLabs запустите: python3 elevenlabs_uploader.py")

        return True
    
    def sync_with_elevenlabs(self):
        """Синхронизировать обновленные данные с ElevenLabs"""
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv('ELEVENLABS_API_KEY') and os.getenv('ELEVENLABS_AGENT_ID'):
            print("\n☁️ Синхронизация с ElevenLabs...")
            try:
                from elevenlabs_uploader_simple import SimpleElevenLabsUploader
                uploader = SimpleElevenLabsUploader()
                
                # Синхронизируем все файлы
                results = uploader.sync_all_files()
                
            except Exception as e:
                print(f"❌ Ошибка синхронизации с ElevenLabs: {e}")
        else:
            print("\nℹ️ Синхронизация с ElevenLabs не настроена")
    
    def get_version_info(self) -> Dict:
        """Получить информацию о текущей версии"""
        if not self.version_history:
            return {'status': 'no_history'}
        
        latest = self.version_history[-1]
        return {
            'current_version': latest['version'],
            'last_update': latest['timestamp'],
            'total_versions': len(self.version_history),
            'total_properties': latest.get('total_properties', 0),
            'total_apartments': latest.get('total_apartments', 0)
        }
    
    def run_monitoring(self, interval_minutes: int = 60):
        """Запустить мониторинг с заданным интервалом"""
        print(f"🚀 Запуск мониторинга (проверка каждые {interval_minutes} минут)")
        print(f"📍 Источник данных: {self.source_url}")
        print(f"📂 Директория данных: {self.data_dir}")
        
        # Выполняем первую проверку
        self.check_and_update()
        
        # Настраиваем расписание
        schedule.every(interval_minutes).minutes.do(self.check_and_update)
        
        print(f"\n⏰ Следующая проверка через {interval_minutes} минут")
        print("Нажмите Ctrl+C для остановки мониторинга\n")
        
        # Запускаем бесконечный цикл
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Мониторинг остановлен")


def sync_to_elevenlabs(changed_files: List[str] = None):
    """Синхронизация обновленных данных с ElevenLabs (v2)

    Args:
        changed_files: Список измененных MD-файлов (опционально)
    """
    try:
        import subprocess

        print("\n☁️  Синхронизация с ElevenLabs (v2)...")

        # Используем новый elevenlabs_sync_v2.py с правильной логикой
        python_executable = sys.executable
        cmd = [python_executable, 'elevenlabs_sync_v2.py']

        # Если есть список измененных файлов, передаем его
        if changed_files:
            changed_files_path = Path('./quarters/.changed_files.txt')
            with open(changed_files_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(changed_files))

            cmd.append('--changed-files')
            cmd.append(str(changed_files_path))

            print(f"   📝 Изменено файлов: {len(changed_files)}")
        else:
            print(f"   📝 Режим: полная синхронизация (проверка по хешам)")

        print(f"   🚀 Запуск: {' '.join(cmd)}")
        
        # Таймаут 10 минут (теперь загружаем только изменённые)
        timeout_seconds = 10 * 60
        
        result = subprocess.run(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
            timeout=timeout_seconds
        )

        if result.returncode == 0:
            print("✅ Синхронизация с ElevenLabs завершена успешно")
            return True
        else:
            print(f"⚠️  Синхронизация завершилась с ошибками (код: {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        print("⚠️  Таймаут синхронизации с ElevenLabs")
        return False
    except Exception as e:
        print(f"❌ Ошибка синхронизации с ElevenLabs: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Мониторинг изменений данных недвижимости')
    parser.add_argument(
        '--check',
        action='store_true',
        help='Выполнить одну проверку и выйти'
    )
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Запустить непрерывный мониторинг'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Интервал проверки в минутах (по умолчанию: 60)'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='Показать информацию о текущей версии'
    )
    parser.add_argument(
        '--url',
        default='https://bir.by/ai/json_ai.php',
        help='URL источника данных'
    )
    parser.add_argument(
        '--upload-to-elevenlabs',
        action='store_true',
        help='Автоматически загружать обновления в ElevenLabs'
    )

    args = parser.parse_args()

    # Создаем монитор
    monitor = PropertyMonitor(source_url=args.url)

    if args.info:
        # Показываем информацию о версии
        info = monitor.get_version_info()
        print("📊 Информация о базе знаний:")
        print(json.dumps(info, ensure_ascii=False, indent=2))
    elif args.monitor:
        # Запускаем мониторинг
        monitor.run_monitoring(interval_minutes=args.interval)
    else:
        # Выполняем одну проверку
        has_changes = monitor.check_and_update()

        # Если есть изменения и включена загрузка в ElevenLabs
        if has_changes and args.upload_to_elevenlabs:
            # Передаем список измененных файлов для инкрементальной загрузки
            sync_to_elevenlabs(changed_files=monitor.changed_md_files)


if __name__ == "__main__":
    main()