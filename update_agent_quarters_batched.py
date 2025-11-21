#!/usr/bin/env python3
"""
Обновление агента ElevenLabs - добавление новых кварталов пакетами
"""
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def main():
    api_key = os.getenv('ELEVENLABS_API_KEY')
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')

    # ID новых кварталов с правильной кодировкой (uploaded at 1763642xxx)
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

    # Добавляем также общие файлы
    general_ids = [
        'kL3zNCHbhtptIq25QNPm',  # 04-baza-znaniy-dlya-konsultaciy
        'rQciMWgeCGRKhgheCzuJ',  # 00-obschie-svedeniya
    ]

    all_ids = new_quarter_ids + general_ids

    print("=" * 60)
    print("🔄 Обновление агента ElevenLabs")
    print("=" * 60)
    print(f"\n📊 Кварталов для добавления: {len(new_quarter_ids)}")
    print(f"📄 Общих файлов: {len(general_ids)}")
    print(f"📝 Всего документов: {len(all_ids)}")

    # Получаем текущую конфигурацию агента
    print("\n🔍 Получение текущей конфигурации агента...")
    agent_url = f'https://api.elevenlabs.io/v1/convai/agents/{agent_id}'
    headers = {'xi-api-key': api_key}

    response = requests.get(agent_url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Ошибка при получении агента: {response.status_code}")
        print(f"   Ответ: {response.text[:200]}")
        return

    agent_data = response.json()
    print("✅ Конфигурация получена")

    # Обновляем knowledge base ids
    print("\n🔧 Обновление knowledge base...")
    agent_data['conversation_config']['knowledge_base'] = {'ids': all_ids}

    # Отправляем обновление
    print("📤 Отправка обновления агенту...")
    update_url = f'https://api.elevenlabs.io/v1/convai/agents/{agent_id}'
    update_headers = {
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }

    try:
        update_response = requests.patch(
            update_url,
            headers=update_headers,
            json=agent_data,
            timeout=60  # 60 секунд таймаут
        )

        if update_response.status_code == 200:
            print("\n" + "=" * 60)
            print("✅ УСПЕХ! Агент обновлен")
            print("=" * 60)
            print(f"✅ Добавлено кварталов: {len(new_quarter_ids)}")
            print(f"✅ Добавлено общих файлов: {len(general_ids)}")
            print(f"✅ Всего документов в агенте: {len(all_ids)}")
            print("=" * 60)
            return True
        else:
            print(f"\n❌ Ошибка обновления: HTTP {update_response.status_code}")
            print(f"   Ответ: {update_response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print("\n⚠️ Таймаут запроса (60 сек)")
        print("   Попробуйте проверить агента вручную - изменения могли быть применены")
        return False
    except Exception as e:
        print(f"\n❌ Ошибка: {str(e)}")
        return False


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
