# ElevenLabs Integration для MM-RAG

## Статус интеграции ✅

Система успешно настроена и работает:

1. **Автоматическая синхронизация с bir.by** - Каждый час с 9:00 до 18:00
2. **Парсинг и структурирование данных** - JSON файлы по кварталам
3. **Загрузка в ElevenLabs Knowledge Base** - 39 документов загружено

## Загруженные документы

В Knowledge Base загружены следующие документы:
- `MM-RAG База Знаний - Все квартиры` - полная база данных
- 18 файлов кварталов с детальной информацией

## Известная проблема

Документы успешно загружены в общий Knowledge Base, но API показывает 0 документов в агенте. Это может быть связано с:
- Асинхронным обновлением на стороне ElevenLabs
- Ограничениями API ключа
- Необходимостью привязки через веб-интерфейс

## Решение

### Вариант 1: Через веб-интерфейс
1. Откройте https://elevenlabs.io/app/conversational-ai
2. Выберите агента "MM-Agent v4"
3. Перейдите в раздел Knowledge Base
4. Добавьте загруженные документы вручную

### Вариант 2: Проверка через время
API может обновляться с задержкой. Проверьте через несколько минут:
```bash
python3 test_elevenlabs_api.py
```

## Файлы проекта

### Основные скрипты
- `sync-with-monitoring.py` - основной скрипт синхронизации
- `elevenlabs_uploader_simple.py` - загрузка файлов в Knowledge Base
- `elevenlabs_agent_updater.py` - привязка документов к агенту
- `link_all_documents.py` - привязка всех документов

### Тестовые скрипты
- `test_elevenlabs_api.py` - проверка API и статуса
- `check_kb_documents.py` - детальная проверка Knowledge Base

### Конфигурация
- `.env` - API ключи (ELEVENLABS_API_KEY, ELEVENLABS_AGENT_ID)
- `cron-update.sh` - скрипт для cron

## Команды

### Ручная синхронизация
```bash
# Проверить и обновить данные с bir.by
python3 sync-with-monitoring.py --check

# Загрузить документы в ElevenLabs
python3 elevenlabs_uploader_simple.py

# Попытаться привязать к агенту
python3 link_all_documents.py
```

### Проверка статуса
```bash
# Проверить cron задания
crontab -l

# Посмотреть логи
tail -50 cron-update.log

# Проверить статус агента
python3 test_elevenlabs_api.py
```

## API Endpoints

- База знаний: `GET/POST https://api.elevenlabs.io/v1/convai/knowledge-base`
- Агент: `GET/PATCH https://api.elevenlabs.io/v1/convai/agents/{agent_id}`

## Важные ID

- Agent ID: `agent_8901k4s5hkbkf7gsf1tk5r0a4g8t`
- Пример Document ID: `TwkSu4qxmhNw8fkpnfch`

## Поддержка

При проблемах проверьте:
1. Наличие API ключей в `.env`
2. Права доступа API ключа
3. Статус ElevenLabs сервисов
4. Логи в `cron-update.log`