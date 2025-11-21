# MM-RAG Sync System - Система синхронизации базы знаний

## Обзор

Система автоматической синхронизации данных недвижимости между:
- Вашим сайтом
- Локальной базой знаний (папка `/quarters`)
- ElevenLabs Conversational AI Knowledge Base

## Установка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка конфигурации

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и добавьте ваши ключи:

```env
# Обязательные параметры для ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_AGENT_ID=your_agent_id

# Опциональные параметры для синхронизации с сайтом
WEBSITE_API_URL=https://your-website.com/api/properties
WEBSITE_API_KEY=your_api_key
```

### 3. Получение API ключей

#### ElevenLabs:
1. Зайдите на https://elevenlabs.io/
2. Создайте аккаунт и агента
3. В настройках агента найдите Agent ID
4. В профиле получите API Key

## Использование

### Ручная синхронизация

#### Синхронизировать всю папку quarters с ElevenLabs:
```bash
python sync-knowledge-base.py
```

#### Синхронизировать конкретный файл:
```bash
python sync-knowledge-base.py --file ./quarters/02-emirats.md
```

#### Принудительное обновление всех файлов:
```bash
python sync-knowledge-base.py --force
```

### Синхронизация с сайтом

```bash
python sync-from-website.py
```

Эта команда:
1. Получает данные с вашего сайта через API
2. Преобразует их в markdown файлы
3. Сохраняет в папку `/quarters`
4. Автоматически синхронизирует с ElevenLabs

### Полная автоматическая синхронизация

```bash
./auto-sync.sh
```

Этот скрипт выполняет:
1. Получение данных с сайта (если настроено)
2. Обновление локальных файлов
3. Синхронизацию с ElevenLabs

### Настройка автоматического запуска

#### Через cron (каждый час):
```bash
./auto-sync.sh --setup-cron
```

#### Через systemd (для production):
```bash
sudo cp mm-rag-sync.service /etc/systemd/system/
sudo systemctl enable mm-rag-sync.timer
sudo systemctl start mm-rag-sync.timer
```

## Как работает синхронизация

### 1. Замена файлов

При синхронизации файла система:
1. Удаляет старую версию из ElevenLabs Knowledge Base
2. Загружает новую версию
3. Сохраняет хеш файла для отслеживания изменений

### 2. Отслеживание изменений

Система использует MD5 хеши файлов (`.sync_hashes.json`) для определения измененных файлов. При обычной синхронизации обновляются только измененные файлы.

### 3. API формат данных с сайта

Ваш API должен возвращать JSON в формате:

```json
[
  {
    "id": 1,
    "name": "Emirates Hills Villa",
    "location": "Dubai, UAE",
    "developer": "Emaar Properties",
    "completion_date": "2024 Q4",
    "apartments": [
      {
        "type": "2 Bedroom",
        "area": 120,
        "price": 450000,
        "floor": "5",
        "rooms": 2
      }
    ],
    "amenities": [
      "Swimming Pool",
      "Gym",
      "Parking"
    ],
    "payment_options": {
      "installment": "36 months interest-free",
      "mortgage": "Available through partner banks"
    },
    "description": "Luxury villa in prime location..."
  }
]
```

## Структура файлов

### Сгенерированные markdown файлы

Каждый объект недвижимости сохраняется в формате:
- Имя файла: `{id}-{name}.md` (например: `02-emirats-hills.md`)
- Содержимое: структурированный markdown с всей информацией

### Пример содержимого файла

```markdown
# Emirates Hills Villa

## Основная информация

**Локация:** Dubai, UAE
**Застройщик:** Emaar Properties
**Срок сдачи:** 2024 Q4

## Доступные квартиры

### 2 Bedroom
- **Площадь:** 120 м²
- **Цена:** 450,000 €
- **Этаж:** 5
- **Комнат:** 2

## Удобства и инфраструктура

- Swimming Pool
- Gym
- Parking

## Условия оплаты

- **Рассрочка:** 36 months interest-free
- **Ипотека:** Available through partner banks

---
*Обновлено: 2024-01-15 14:30*
```

## Отладка и логирование

### Просмотр логов cron:
```bash
tail -f /tmp/mm-rag-sync.log
```

### Проверка статуса в ElevenLabs:
```bash
python -c "from sync_knowledge_base import *; sync = ElevenLabsKnowledgeSync('KEY', 'ID'); print(sync.list_documents())"
```

### Очистка всей базы знаний:
```bash
python -c "from sync_knowledge_base import *; sync = ElevenLabsKnowledgeSync('KEY', 'ID'); [sync.delete_document(d['name']) for d in sync.list_documents()]"
```

## Безопасность

- **Никогда** не коммитьте файл `.env` в git
- Используйте переменные окружения для production
- Ограничьте доступ к API ключам
- Регулярно ротируйте ключи

## Поддержка

При возникновении проблем проверьте:
1. Правильность API ключей в `.env`
2. Доступность API endpoints
3. Формат возвращаемых данных с сайта
4. Логи в `/tmp/mm-rag-sync.log`