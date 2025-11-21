#!/usr/bin/env python3
"""
Загрузка MD файлов в ElevenLabs с правильной кодировкой UTF-8
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import codecs

load_dotenv()

def upload_md_file_with_correct_encoding(file_path, api_key):
    """Загружает MD файл в ElevenLabs с правильной кодировкой"""
    url = "https://api.elevenlabs.io/v1/convai/knowledge-base"
    headers = {"xi-api-key": api_key}

    # Читаем содержимое файла с явным указанием UTF-8
    with codecs.open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Название из файла
    name = Path(file_path).stem

    # Загружаем как текстовый файл с правильной кодировкой
    # Используем явное указание charset в Content-Type
    files = {
        'file': (f'{name}.txt', content.encode('utf-8'), 'text/plain; charset=utf-8')
    }
    data = {
        'name': name
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code in [200, 201]:
        result = response.json()
        kb_id = result.get('id', 'N/A')
        return True, kb_id, name
    else:
        print(f"      Статус: {response.status_code}, Ответ: {response.text[:200]}")
        return False, None, name


def main():
    api_key = os.getenv('ELEVENLABS_API_KEY')
    quarters_dir = Path('/Users/admin/MM-RAG/quarters')

    # Список файлов кварталов для загрузки
    quarter_files = [
        '02-emirats.md',
        '10-Tropicheskie-ostrova.md',
        '11-Avstraliya-i-Okeaniya.md',
        '12-Zapadnaya-Evropa.md',
        '16-Rodnaya-strana.md',
        '18-Chempionov.md',
        '19-Yuzhnaya-Evropa.md',
        '20-Mirovyh-tantsev.md',
        '21-Zapadnyy.md',
        '22-Tsentralnaya-Evropa.md',
        '23-Evraziya.md',
        '25-Aziya.md',
        '26-Afrika.md',
        '27-Happy-Planet.md',
        '29-Severnaya-Evropa.md',
        '30-Severnaya-Amerika.md',
        '7-Sredizemnomorskiy.md',
        '9-Yuzhnaya-Amerika.md',
        # Дополнительные файлы
        '00-obschie-svedeniya.md',
        '04-baza-znaniy-dlya-konsultaciy.md',
    ]

    print("=" * 60)
    print("📤 Загрузка MD файлов с правильной кодировкой UTF-8")
    print("=" * 60)
    print(f"\n📂 Папка: {quarters_dir}")
    print(f"📄 Файлов для загрузки: {len(quarter_files)}\n")

    uploaded_ids = []
    failed = []

    for i, filename in enumerate(quarter_files, 1):
        file_path = quarters_dir / filename

        if not file_path.exists():
            print(f"⚠️ {i}/{len(quarter_files)} - Файл не найден: {filename}")
            failed.append(filename)
            continue

        print(f"📤 {i}/{len(quarter_files)} - Загрузка: {filename}")
        success, kb_id, name = upload_md_file_with_correct_encoding(file_path, api_key)

        if success:
            print(f"   ✅ Загружено (ID: {kb_id})")
            uploaded_ids.append(kb_id)
        else:
            print(f"   ❌ Ошибка")
            failed.append(filename)

    print("\n" + "=" * 60)
    print("📊 Результаты:")
    print(f"✅ Загружено: {len(uploaded_ids)}/{len(quarter_files)}")

    if failed:
        print(f"❌ Не загружено: {len(failed)}")
        for f in failed:
            print(f"   - {f}")

    print("=" * 60)

    # Сохраняем ID для следующего шага
    if uploaded_ids:
        with open('/Users/admin/MM-RAG/uploaded_kb_ids_correct.txt', 'w') as f:
            f.write('\n'.join(uploaded_ids))
        print(f"\n✅ ID документов сохранены в uploaded_kb_ids_correct.txt")

    return uploaded_ids


if __name__ == "__main__":
    try:
        ids = main()
        print(f"\n✨ Готово! Загружено {len(ids)} документов с правильной кодировкой")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
