#!/usr/bin/env python3
"""
Инкрементальное добавление кварталов к агенту
"""
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def get_current_kb_ids(api_key, agent_id):
    """Получить текущие KB IDs агента"""
    agent_url = f'https://api.elevenlabs.io/v1/convai/agents/{agent_id}'
    response = requests.get(agent_url, headers={'xi-api-key': api_key})

    if response.status_code == 200:
        agent_data = response.json()
        kb_config = agent_data.get('conversation_config', {}).get('knowledge_base', {})
        return kb_config.get('ids', [])
    return []

def update_agent_kb(api_key, agent_id, kb_ids):
    """Обновить KB IDs агента"""
    agent_url = f'https://api.elevenlabs.io/v1/convai/agents/{agent_id}'

    # Получаем текущую конфигурацию
    response = requests.get(agent_url, headers={'xi-api-key': api_key})
    if response.status_code != 200:
        return False, f"Ошибка получения агента: {response.status_code}"

    agent_data = response.json()
    agent_data['conversation_config']['knowledge_base'] = {'ids': kb_ids}

    # Обновляем
    update_response = requests.patch(
        agent_url,
        headers={'xi-api-key': api_key, 'Content-Type': 'application/json'},
        json=agent_data,
        timeout=30
    )

    if update_response.status_code == 200:
        return True, "Успех"
    else:
        return False, f"HTTP {update_response.status_code}: {update_response.text[:200]}"

def main():
    api_key = os.getenv('ELEVENLABS_API_KEY')
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')

    # ID новых кварталов (18 штук)
    new_quarter_ids = [
        'qXtJqqEp0ZkcmJX4gc6v',  # 19-Yuzhnaya-Evropa
        'YKvNKCYwODU8AwJI7Muc',  # 26-Afrika
        'wKmcKNykVwd3TFIxmQdc',  # 21-Zapadnyy
        'DLY9LrhEzIzQzGsDOYlC',  # 10-Tropicheskie-ostrova
        'UmvXAJUR6N8jFbIQIU9o',  # 30-Severnaya-Amerika
        'LBIOsPT66B1gdKbHGv2R',  # 27-Happy-Planet
        'be45mka7XvHxmtbaOKDR',  # 20-Mirovyh-tantsev
        'Nn84sS7X6Piy9Z1UtTdw',  # 29-Severnaya-Evropa
        'e4V9Igwsug2omLaivTBc',  # 7-Sredizemnomorskiy
        'fr3uFF45uBR5uIKDx5aP',  # 12-Zapadnaya-Evropa
        'VJKupwQM3Ly22RMZj8kO',  # 18-Chempionov
        'sYnqGkVVXN6U7ScbsP8N',  # 9-Yuzhnaya-Amerika
        'ebURL7MgqknbKVxkY995',  # 22-Tsentralnaya-Evropa
        'MQH2CsUQj6IHJAgEiSd3',  # 25-Aziya
        'NYwYJ0wvDeSLj0BMZJOy',  # 16-Rodnaya-strana
        'qWSLSMQhjJggi9vmOe5Q',  # 02-Emirats
        'G9f2bpyZmIEpUPI6EVrx',  # 23-Evraziya
        'e7XBCzszhGnL4s0eaKmg',  # 11-Avstraliya-i-Okeaniya
    ]

    # Общие файлы
    general_ids = [
        'kL3zNCHbhtptIq25QNPm',  # 04-baza-znaniy-dlya-konsultaciy
        'rQciMWgeCGRKhgheCzuJ',  # 00-obschie-svedeniya
    ]

    print("=" * 60)
    print("🔄 Инкрементальное обновление агента")
    print("=" * 60)

    # Шаг 1: Сбросить текущие KB IDs (удалить старые кварталы)
    print("\n🗑️ Шаг 1: Очистка старых кварталов...")
    success, message = update_agent_kb(api_key, agent_id, [])
    if success:
        print("✅ Старые кварталы удалены")
        time.sleep(2)
    else:
        print(f"❌ Ошибка: {message}")
        return False

    # Шаг 2: Добавить общие файлы
    print("\n📄 Шаг 2: Добавление общих файлов...")
    success, message = update_agent_kb(api_key, agent_id, general_ids)
    if success:
        print(f"✅ Добавлено общих файлов: {len(general_ids)}")
        time.sleep(2)
    else:
        print(f"❌ Ошибка: {message}")
        return False

    # Шаг 3: Добавить кварталы пакетами по 5
    batch_size = 5
    current_ids = general_ids.copy()

    for i in range(0, len(new_quarter_ids), batch_size):
        batch = new_quarter_ids[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(new_quarter_ids) + batch_size - 1) // batch_size

        print(f"\n📦 Шаг 3.{batch_num}: Добавление пакета {batch_num}/{total_batches} ({len(batch)} кварталов)...")

        current_ids.extend(batch)
        success, message = update_agent_kb(api_key, agent_id, current_ids)

        if success:
            print(f"✅ Пакет добавлен (всего документов в агенте: {len(current_ids)})")
            time.sleep(2)
        else:
            print(f"❌ Ошибка: {message}")
            print(f"⚠️ Частично добавлено: {len(current_ids) - len(batch)} документов")
            return False

    print("\n" + "=" * 60)
    print("✅ УСПЕХ! Агент полностью обновлен")
    print("=" * 60)
    print(f"✅ Общих файлов: {len(general_ids)}")
    print(f"✅ Кварталов: {len(new_quarter_ids)}")
    print(f"✅ Всего документов: {len(current_ids)}")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✨ Готово!")
        else:
            print("\n⚠️ Завершено с ошибками")
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
