# Настройка браузерной автоматизации LinkedIn

## Обзор

Вместо использования LinkedIn API, система использует браузерную автоматизацию для публикации вакансий. Это позволяет обойти ограничения API и работать напрямую с веб-интерфейсом LinkedIn.

## Требования

### Системные требования
- Python 3.8+
- Google Chrome браузер
- Стабильное интернет-соединение

### Python зависимости
```bash
pip install selenium webdriver-manager playwright undetected-chromedriver
```

## Установка

### 1. Установка Chrome WebDriver
```bash
# Автоматическая установка через webdriver-manager
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

### 2. Установка Playwright (опционально)
```bash
playwright install chromium
```

### 3. Настройка переменных окружения
```bash
# Создайте файл .env
LINKEDIN_EMAIL=your-linkedin-email@example.com
LINKEDIN_PASSWORD=your-linkedin-password
CHROME_HEADLESS=false
```

## Конфигурация

### Основные настройки браузера
```python
# В linkedin_browser_automation.py
options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
```

### Настройки для обхода обнаружения
- Использование `undetected-chromedriver`
- Скрытие признаков автоматизации
- Эмуляция человеческого поведения
- Случайные задержки между действиями

## Использование

### Базовое использование
```python
from automation.workflows.linkedin_browser_automation import LinkedInBrowserAutomation

# Инициализация
automation = LinkedInBrowserAutomation(headless=False)

# Данные вакансии
vacancy_data = {
    'title': 'Senior Python Developer',
    'company': 'TechCorp',
    'location': 'San Francisco, CA',
    'requirements': 'Python, Django, React, 5+ years experience'
}

# Публикация вакансии
result = automation.post_job_vacancy(
    vacancy_data, 
    email="your-email@example.com", 
    password="your-password"
)
```

### Использование через Claude команды
```bash
/post-vacancy --title "Senior Developer" --company "TechCorp" --location "San Francisco"
```

## Безопасность

### Хранение учетных данных
- Используйте переменные окружения
- Не храните пароли в коде
- Регулярно обновляйте пароли
- Используйте двухфакторную аутентификацию

### Рекомендации по безопасности
```python
# Безопасное получение учетных данных
import os
from getpass import getpass

email = os.getenv('LINKEDIN_EMAIL')
password = os.getenv('LINKEDIN_PASSWORD') or getpass('LinkedIn password: ')
```

## Устранение неполадок

### Частые проблемы

#### 1. Ошибка "Chrome driver not found"
```bash
# Решение: Установите Chrome WebDriver
pip install webdriver-manager
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

#### 2. Ошибка "Element not found"
- Проверьте селекторы CSS
- Убедитесь, что страница загрузилась полностью
- Добавьте дополнительные задержки

#### 3. Ошибка "Login failed"
- Проверьте правильность email и пароля
- Убедитесь, что аккаунт не заблокирован
- Попробуйте войти вручную в браузере

#### 4. Ошибка "Captcha detected"
- Используйте `undetected-chromedriver`
- Добавьте случайные задержки
- Рассмотрите использование прокси

### Отладка
```python
# Включение подробного логирования
import logging
logging.basicConfig(level=logging.DEBUG)

# Сохранение скриншотов при ошибках
automation.driver.save_screenshot('error_screenshot.png')
```

## Оптимизация

### Улучшение производительности
```python
# Использование headless режима
automation = LinkedInBrowserAutomation(headless=True)

# Оптимизация настроек браузера
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument('--disable-plugins')
```

### Улучшение надежности
```python
# Добавление повторных попыток
import time
from functools import wraps

def retry_on_failure(max_attempts=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
```

## Мониторинг

### Логирование действий
```python
# Настройка логирования
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_automation.log'),
        logging.StreamHandler()
    ]
)
```

### Отслеживание метрик
```python
# Сохранение метрик в базу данных
def track_automation_metrics(action, success, duration):
    conn = sqlite3.connect('database/automation_metrics.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO automation_metrics (action, success, duration, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (action, success, duration, datetime.now()))
    
    conn.commit()
    conn.close()
```

## Альтернативы

### Playwright (более современная альтернатива)
```python
from playwright.sync_api import sync_playwright

def post_job_with_playwright(vacancy_data, email, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Логин в LinkedIn
        page.goto('https://www.linkedin.com/login')
        page.fill('#username', email)
        page.fill('#password', password)
        page.click('button[type="submit"]')
        
        # Навигация к публикации вакансии
        page.goto('https://www.linkedin.com/talent/post-a-job')
        
        # Заполнение формы
        page.fill('[data-test-id="job-title-input"]', vacancy_data['title'])
        page.fill('[data-test-id="job-location-input"]', vacancy_data['location'])
        
        browser.close()
```

### Selenium с дополнительными возможностями
```python
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# Эмуляция человеческого поведения
def human_like_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

# Случайные движения мыши
def random_mouse_movement(driver):
    actions = ActionChains(driver)
    actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100))
    actions.perform()
```

## Заключение

Браузерная автоматизация предоставляет гибкий способ работы с LinkedIn без необходимости использования API. Важно соблюдать правила использования LinkedIn и не злоупотреблять автоматизацией.

### Рекомендации
- Используйте разумные задержки между действиями
- Не публикуйте слишком много вакансий за короткое время
- Регулярно обновляйте селекторы CSS
- Мониторьте логи для выявления проблем
- Имейте план B на случай блокировки аккаунта 