#!/usr/bin/env python3
"""
Автоматическое обновление агента ElevenLabs через Selenium
ВАЖНО: Этот скрипт НЕ изменяет существующие рабочие файлы
"""
import os
import time
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

load_dotenv()

class ElevenLabsAgentUpdater:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.agent_id = os.getenv('ELEVENLABS_AGENT_ID')

        if not self.api_key or not self.agent_id:
            raise ValueError("❌ ELEVENLABS_API_KEY или ELEVENLABS_AGENT_ID не найдены в .env")

        # Новые 18 кварталов с правильной кодировкой
        self.new_quarters = [
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
        self.general_files = [
            ('04-baza-znaniy', 'kL3zNCHbhtptIq25QNPm'),
            ('00-obschie-svedeniya', 'rQciMWgeCGRKhgheCzuJ'),
        ]

        self.all_docs = self.new_quarters + self.general_files
        self.driver = None

    def setup_driver(self):
        """Настройка Chrome WebDriver"""
        print("🔧 Настройка браузера...")

        chrome_options = Options()
        # Раскомментируй следующую строку для headless режима (без GUI)
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        print("✅ Браузер запущен")

    def login_if_needed(self):
        """Проверка необходимости входа и выполнение входа"""
        agent_url = f"https://elevenlabs.io/app/conversational-ai/agents/{self.agent_id}/edit"

        print(f"\n🌐 Открытие страницы агента...")
        self.driver.get(agent_url)
        time.sleep(3)

        # Проверяем, нужен ли вход
        current_url = self.driver.current_url

        if 'login' in current_url or 'sign-in' in current_url:
            print("\n⚠️  Требуется вход в аккаунт ElevenLabs")
            print("=" * 60)
            print("📝 ИНСТРУКЦИЯ:")
            print("1. Войдите в свой аккаунт ElevenLabs в открывшемся браузере")
            print("2. После успешного входа нажмите Enter здесь")
            print("=" * 60)
            input("\nНажмите Enter после входа в систему...")

            # Переходим обратно на страницу агента
            self.driver.get(agent_url)
            time.sleep(3)

        print("✅ Страница агента открыта")

    def get_current_kb_via_api(self):
        """Получить текущие KB документы через API"""
        url = f'https://api.elevenlabs.io/v1/convai/agents/{self.agent_id}'
        response = requests.get(url, headers={'xi-api-key': self.api_key}, timeout=30)

        if response.status_code == 200:
            agent_data = response.json()
            kb_config = agent_data.get('conversation_config', {}).get('knowledge_base', {})

            if isinstance(kb_config, dict):
                return kb_config.get('ids', [])
            elif isinstance(kb_config, list):
                return kb_config
        return []

    def add_documents_via_ui(self):
        """Добавление документов через UI"""
        print("\n📤 Добавление документов через веб-интерфейс...")
        print("=" * 60)

        # Получаем текущий список
        current_ids = self.get_current_kb_via_api()
        print(f"📊 Текущих документов в агенте: {len(current_ids)}")

        # Определяем, какие нужно добавить
        to_add = []
        for name, doc_id in self.all_docs:
            if doc_id not in current_ids:
                to_add.append((name, doc_id))

        if not to_add:
            print("✅ Все документы уже добавлены!")
            return True

        print(f"📝 Документов для добавления: {len(to_add)}")
        print("\n⚠️  ВАЖНО: Сейчас откроется страница редактирования агента")
        print("Вам нужно будет вручную добавить документы из Knowledge Base")
        print("\nСписок документов для добавления:")
        for i, (name, doc_id) in enumerate(to_add, 1):
            print(f"  {i}. {name}")

        print("\n" + "=" * 60)
        print("📝 ИНСТРУКЦИЯ ПО ДОБАВЛЕНИЮ:")
        print("1. В открывшемся браузере найдите раздел 'Knowledge Base'")
        print("2. Нажмите кнопку 'Add documents' или '+'")
        print("3. Выберите документы из списка выше")
        print("4. Сохраните изменения")
        print("5. Вернитесь сюда и нажмите Enter")
        print("=" * 60)

        input("\nНажмите Enter после добавления документов...")

        # Проверяем результат через API
        time.sleep(2)
        updated_ids = self.get_current_kb_via_api()

        print(f"\n📊 Документов в агенте после обновления: {len(updated_ids)}")

        success_count = 0
        for name, doc_id in to_add:
            if doc_id in updated_ids:
                success_count += 1

        print(f"✅ Успешно добавлено: {success_count}/{len(to_add)}")

        return success_count == len(to_add)

    def run(self):
        """Основной процесс"""
        try:
            print("=" * 60)
            print("🤖 Selenium автоматизация обновления агента ElevenLabs")
            print("=" * 60)

            self.setup_driver()
            self.login_if_needed()
            success = self.add_documents_via_ui()

            if success:
                print("\n" + "=" * 60)
                print("✅ УСПЕХ! Все документы добавлены")
                print("=" * 60)
                print("\n📊 Итого:")
                print(f"  - Кварталов: {len(self.new_quarters)}")
                print(f"  - Общих файлов: {len(self.general_files)}")
                print(f"  - Всего: {len(self.all_docs)}")
                print("\n✨ Теперь автоматическая синхронизация будет работать!")
            else:
                print("\n⚠️  Некоторые документы не были добавлены")
                print("Проверьте вручную на странице агента")

            return success

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            if self.driver:
                print("\n⏳ Закрытие браузера через 5 секунд...")
                time.sleep(5)
                self.driver.quit()
                print("✅ Браузер закрыт")


def main():
    """Точка входа"""
    print("\n⚠️  ВАЖНО: Этот скрипт откроет браузер Chrome")
    print("Убедитесь, что у вас установлен Chrome")
    print("\nПродолжить? (y/n): ", end='')

    response = input().strip().lower()
    if response != 'y':
        print("Отменено")
        return

    updater = ElevenLabsAgentUpdater()
    success = updater.run()

    if success:
        print("\n✨ Готово!")
    else:
        print("\n⚠️  Завершено с ошибками")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
