#!/usr/bin/env python3
"""
Утилита для разовой чистки старых версий документов в ElevenLabs Knowledge Base

Использование:
    python3 cleanup_old_kb_docs.py --dry-run    # Показать что будет удалено
    python3 cleanup_old_kb_docs.py --confirm    # Выполнить удаление
"""

import os
import json
import requests
import re
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()


class KnowledgeBaseCleanup:
    """Утилита для чистки старых версий документов"""

    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')

        if not self.api_key:
            raise ValueError("❌ ELEVENLABS_API_KEY не найден в .env файле")

        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {"xi-api-key": self.api_key}

    def get_all_documents(self) -> List[Dict]:
        """Получить все документы из Knowledge Base"""
        all_docs = []
        page = 0

        print("📚 Получение списка документов...")

        while True:
            url = f"{self.base_url}/convai/knowledge-base?page_size=100&page={page}"

            try:
                response = requests.get(url, headers=self.headers, timeout=30)

                if response.status_code != 200:
                    break

                data = response.json()
                docs = data.get('documents', data.get('knowledge_bases', []))

                if not docs:
                    break

                all_docs.extend(docs)

                if not data.get('has_more', False):
                    break

                page += 1

            except Exception as e:
                print(f"❌ Ошибка: {e}")
                break

        print(f"   Найдено документов: {len(all_docs)}\n")
        return all_docs

    def analyze_versions(self, all_docs: List[Dict]) -> Dict:
        """
        Анализировать версии документов

        Returns:
            {
                'to_delete': [...],  # Документы для удаления
                'to_keep': [...],    # Документы для сохранения
                'stats': {...}       # Статистика
            }
        """
        grouped = defaultdict(list)

        # Группируем по базовому имени
        for doc in all_docs:
            name = doc.get('name', '')

            # Пропускаем системные
            if any(x in name.lower() for x in ['system', 'elevenlabs_rag', 'prompt', 'instructions']):
                continue

            # Извлекаем базовое имя
            base_name = re.sub(r'-v\d+|-\d{4}-\d{2}-\d{2}', '', name)
            base_name = re.sub(r'\.(txt|md|html)$', '', base_name)

            grouped[base_name].append(doc)

        # Анализируем
        to_delete = []
        to_keep = []
        multiple_versions = {}

        for base_name, versions in grouped.items():
            if len(versions) == 1:
                to_keep.extend(versions)
            else:
                # Есть несколько версий
                multiple_versions[base_name] = len(versions)

                # Сортируем по дате
                versions_sorted = sorted(
                    versions,
                    key=lambda x: x.get('metadata', {}).get('created_at_unix_secs', 0),
                    reverse=True
                )

                # Сохраняем самую новую
                to_keep.append(versions_sorted[0])

                # Остальные - удаляем
                for old_version in versions_sorted[1:]:
                    to_delete.append(old_version)

        stats = {
            'total_documents': len(all_docs),
            'unique_base_names': len(grouped),
            'documents_with_multiple_versions': len(multiple_versions),
            'versions_to_delete': len(to_delete),
            'versions_to_keep': len(to_keep),
            'multiple_versions_detail': multiple_versions
        }

        return {
            'to_delete': to_delete,
            'to_keep': to_keep,
            'stats': stats
        }

    def print_analysis(self, analysis: Dict):
        """Вывести результаты анализа"""
        stats = analysis['stats']
        to_delete = analysis['to_delete']

        print("=" * 70)
        print("📊 АНАЛИЗ ВЕРСИЙ ДОКУМЕНТОВ")
        print("=" * 70)
        print(f"Всего документов: {stats['total_documents']}")
        print(f"Уникальных файлов (без версий): {stats['unique_base_names']}")
        print(f"Файлов с несколькими версиями: {stats['documents_with_multiple_versions']}")
        print(f"Версий для удаления: {stats['versions_to_delete']}")
        print(f"Версий для сохранения: {stats['versions_to_keep']}")

        if stats['multiple_versions_detail']:
            print("\n📋 Файлы с несколькими версиями:")
            for base_name, count in sorted(
                stats['multiple_versions_detail'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]:
                print(f"   {base_name[:50]:50} - {count} версий")

            if len(stats['multiple_versions_detail']) > 20:
                print(f"   ... и еще {len(stats['multiple_versions_detail']) - 20}")

        if to_delete:
            print(f"\n🗑️  ДОКУМЕНТЫ ДЛЯ УДАЛЕНИЯ (всего {len(to_delete)}):")
            print(f"   Первые 20:")
            for i, doc in enumerate(to_delete[:20], 1):
                name = doc.get('name', 'Unknown')
                doc_id = doc.get('id', '')
                created = doc.get('metadata', {}).get('created_at_unix_secs', 0)

                if created:
                    date_str = datetime.fromtimestamp(created).strftime('%Y-%m-%d')
                else:
                    date_str = 'N/A'

                print(f"   {i:2}. {name[:50]:50} | {date_str} | {doc_id[:15]}...")

            if len(to_delete) > 20:
                print(f"   ... и еще {len(to_delete) - 20} документов")

        print("=" * 70)

    def delete_documents(self, to_delete: List[Dict]) -> int:
        """Удалить документы"""
        deleted_count = 0

        print(f"\n🗑️  Удаление {len(to_delete)} документов...")

        for i, doc in enumerate(to_delete, 1):
            doc_id = doc.get('id')
            name = doc.get('name', 'Unknown')

            print(f"  {i}/{len(to_delete)} - {name[:50]:50}", end=" ")

            url = f"{self.base_url}/convai/knowledge-base/{doc_id}"

            try:
                response = requests.delete(url, headers=self.headers, timeout=30)

                if response.status_code in [200, 204]:
                    deleted_count += 1
                    print("✅")
                else:
                    print(f"❌ (код {response.status_code})")

            except Exception as e:
                print(f"❌ ({str(e)[:30]})")

            # Пауза между удалениями
            if i < len(to_delete):
                import time
                time.sleep(0.5)

        return deleted_count

    def run(self, dry_run: bool = True):
        """
        Выполнить чистку

        Args:
            dry_run: Если True, только показать анализ без удаления
        """
        print("=" * 70)
        print("🧹 УТИЛИТА ЧИСТКИ KNOWLEDGE BASE")
        print("=" * 70)
        print()

        # Получаем все документы
        all_docs = self.get_all_documents()

        if not all_docs:
            print("ℹ️  Документы не найдены")
            return

        # Анализируем
        analysis = self.analyze_versions(all_docs)

        # Выводим анализ
        self.print_analysis(analysis)

        # Выполняем удаление
        to_delete = analysis['to_delete']

        if not to_delete:
            print("\n✅ Старых версий не найдено, чистка не требуется!")
            return

        if dry_run:
            print("\n⚠️  РЕЖИМ DRY-RUN: Документы НЕ будут удалены")
            print("   Для реального удаления запустите с флагом --confirm")
        else:
            # Подтверждение
            print(f"\n⚠️  ВНИМАНИЕ! Будет удалено {len(to_delete)} документов!")
            print("   Это действие необратимо!")

            response = input("\n   Продолжить? (yes/no): ").strip().lower()

            if response != 'yes':
                print("\n❌ Отменено пользователем")
                return

            # Удаляем
            deleted_count = self.delete_documents(to_delete)

            print("\n" + "=" * 70)
            print(f"✅ ЧИСТКА ЗАВЕРШЕНА!")
            print(f"   Удалено документов: {deleted_count}/{len(to_delete)}")
            print("=" * 70)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Чистка старых версий документов в ElevenLabs Knowledge Base',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  %(prog)s --dry-run    # Показать что будет удалено (безопасно)
  %(prog)s --confirm    # Выполнить удаление (требует подтверждения)
        """
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dry-run', action='store_true', help='Только анализ, без удаления')
    group.add_argument('--confirm', action='store_true', help='Выполнить удаление с подтверждением')

    args = parser.parse_args()

    try:
        cleanup = KnowledgeBaseCleanup()
        cleanup.run(dry_run=args.dry_run)
        return 0
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
