#!/usr/bin/env python3
"""
Добавление документов к агенту по одному
"""
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def get_current_agent_kb(api_key, agent_id):
    """Получить текущие KB IDs агента"""
    url = f'https://api.elevenlabs.io/v1/convai/agents/{agent_id}'
    response = requests.get(url, headers={'xi-api-key': api_key}, timeout=30)

    if response.status_code == 200:
        agent_data = response.json()
        kb_config = agent_data.get('conversation_config', {}).get('knowledge_base', {})

        # Может быть {'ids': [...]} или просто [...]
        if isinstance(kb_config, dict):
            return kb_config.get('ids', [])
        elif isinstance(kb_config, list):
            return kb_config
        return []
    return []

def update_agent_kb(api_key, agent_id, kb_ids):
    """Обновить KB IDs агента"""
    url = f'https://api.elevenlabs.io/v1/convai/agents/{agent_id}'

    # Получаем полную конфигурацию
    response = requests.get(url, headers={'xi-api-key': api_key}, timeout=30)
    if response.status_code != 200:
        return False, f"Ошибка GET: {response.status_code}"

    agent_data = response.json()

    # Обновляем только KB
    agent_data['conversation_config']['knowledge_base'] = {'ids': kb_ids}

    # Отправляем PATCH
    headers = {'xi-api-key': api_key, 'Content-Type': 'application/json'}
    patch_response = requests.patch(url, headers=headers, json=agent_data, timeout=30)

    if patch_response.status_code == 200:
        return True, "OK"
    else:
        return False, f"HTTP {patch_response.status_code}: {patch_response.text[:150]}"

def main():
    api_key = os.getenv('ELEVENLABS_API_KEY')
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')

    # Новые 18 кварталов
    new_quarters = [
        ('19-Yuzhnaya-Evropa', 'qXtJqqEp0ZkcmJX4gc6v'),
        ('26-Afrika', 'YKvNKCYwODU8AwJI7Muc'),
        ('21-Zapadnyy', 'wKmcKNykVwd3TFIxmQdc'),
        ('10-Tropicheskie-ostrova', 'DLY9LrhEzIzQzGsDOYlC'),
        ('30-Severnaya-Amerika', 'UmvXAJUR6N8jFbIQIU9o'),
        ('27-Happy-Planet', 'LBIOsPT66B1gdKbHGv2R'),
        ('20-Mirovyh-tantsev', 'be45mka7XvHxmtbaOKDR'),
        ('29-Severnaya-Evropa', 'Nn84sS7X6Piy9Z1UtTdw'),
        ('7-Sredizemnomorskiy', 'e4V9Igwsug2omLaivTBc'),
        ('12-Zapadnaya-Evropa', 'fr3uFF45uBR5uIKDx5aP'),
        ('18-Chempionov', 'VJKupwQM3Ly22RMZj8kO'),
        ('9-Yuzhnaya-Amerika', 'sYnqGkVVXN6U7ScbsP8N'),
        ('22-Tsentralnaya-Evropa', 'ebURL7MgqknbKVxkY995'),
        ('25-Aziya', 'MQH2CsUQj6IHJAgEiSd3'),
        ('16-Rodnaya-strana', 'NYwYJ0wvDeSLj0BMZJOy'),
        ('02-Emirats', 'qWSLSMQhjJggi9vmOe5Q'),
        ('23-Evraziya', 'G9f2bpyZmIEpUPI6EVrx'),
        ('11-Avstraliya-i-Okeaniya', 'e7XBCzszhGnL4s0eaKmg'),
    ]

    # Общие файлы
    general_files = [
        ('04-baza-znaniy', 'kL3zNCHbhtptIq25QNPm'),
        ('00-obschie-svedeniya', 'rQciMWgeCGRKhgheCzuJ'),
    ]

    all_docs = new_quarters + general_files

    print("=" * 60)
    print("🔄 Добавление документов по одному")
    print("=" * 60)

    # Получаем текущий список
    print("\n📋 Получение текущих документов агента...")
    current_ids = get_current_agent_kb(api_key, agent_id)
    print(f"   Текущих документов: {len(current_ids)}")

    # Начинаем с текущего списка
    updated_ids = current_ids.copy()

    success_count = 0
    failed = []

    print(f"\n📤 Добавление {len(all_docs)} документов...\n")

    for i, (name, doc_id) in enumerate(all_docs, 1):
        # Проверяем, нет ли уже
        if doc_id in updated_ids:
            print(f"⏭️  {i}/{len(all_docs)} - {name} (уже добавлен)")
            success_count += 1
            continue

        # Добавляем новый ID
        updated_ids.append(doc_id)

        print(f"📤 {i}/{len(all_docs)} - Добавление: {name}")

        try:
            success, message = update_agent_kb(api_key, agent_id, updated_ids)

            if success:
                print(f"   ✅ Успешно (всего в агенте: {len(updated_ids)})")
                success_count += 1
                time.sleep(2)  # Пауза между запросами
            else:
                print(f"   ❌ Ошибка: {message}")
                # Откатываем изменение
                updated_ids.remove(doc_id)
                failed.append((name, doc_id, message))

                # Если timeout - увеличиваем паузу
                if 'timeout' in message.lower():
                    print("   ⏸️  Пауза 10 сек из-за timeout...")
                    time.sleep(10)

        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Exception: {error_msg[:100]}")
            updated_ids.remove(doc_id)
            failed.append((name, doc_id, error_msg))

            if 'timeout' in error_msg.lower():
                print("   ⏸️  Пауза 10 сек из-за timeout...")
                time.sleep(10)

    print("\n" + "=" * 60)
    print("📊 Результаты:")
    print("=" * 60)
    print(f"✅ Успешно добавлено: {success_count}/{len(all_docs)}")
    print(f"📝 Всего документов в агенте: {len(updated_ids)}")

    if failed:
        print(f"\n❌ Не удалось добавить: {len(failed)}")
        for name, doc_id, msg in failed:
            print(f"   - {name}: {msg[:80]}")

    print("=" * 60)

    return success_count == len(all_docs)


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✨ Готово! Все документы добавлены")
        else:
            print("\n⚠️ Завершено с ошибками")
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
