# Selenium автоматизация обновления агента ElevenLabs

## Что это?

Скрипт `selenium_update_agent.py` автоматизирует процесс добавления документов Knowledge Base к агенту ElevenLabs через веб-интерфейс.

## Зачем нужен?

API ElevenLabs имеет проблему с PATCH endpoint - он не может обработать обновление агента даже с 1 документом (timeout >30 сек). Единственный рабочий способ - добавление через веб-интерфейс.

## Установка

Все зависимости уже установлены:
```bash
# Selenium уже установлен в venv
```

## Использование

```bash
# Запуск скрипта
/Users/admin/MM-RAG/venv/bin/python3 /Users/admin/MM-RAG/selenium_update_agent.py
```

## Процесс работы

1. **Запуск браузера**: Скрипт откроет Chrome
2. **Вход в аккаунт**: Если нужно - войдите в ElevenLabs
3. **Открытие страницы агента**: Автоматически откроется страница редактирования
4. **Добавление документов**: Следуйте инструкциям в консоли
5. **Проверка**: Скрипт проверит через API, что все документы добавлены

## Что добавится?

### 18 кварталов:
1. 19-Yuzhnaya-Evropa
2. 26-Afrika
3. 21-Zapadnyy
4. 10-Tropicheskie-ostrova
5. 30-Severnaya-Amerika
6. 27-Happy-Planet
7. 20-Mirovyh-tantsev
8. 29-Severnaya-Evropa
9. 7-Sredizemnomorskiy
10. 12-Zapadnaya-Evropa
11. 18-Chempionov
12. 9-Yuzhnaya-Amerika
13. 22-Tsentralnaya-Evropa
14. 25-Aziya
15. 16-Rodnaya-strana
16. 02-Emirats
17. 23-Evraziya
18. 11-Avstraliya-i-Okeaniya

### 2 общих файла:
19. 04-baza-znaniy
20. 00-obschie-svedeniya

## Безопасность

✅ **Скрипт НЕ изменяет существующие файлы:**
- `elevenlabs_auto_sync.py` - не трогается
- `cron-update.sh` - не трогается
- `sync-with-monitoring.py` - не трогается
- Все остальные рабочие файлы - не трогаются

✅ **Только чтение через API** для проверки статуса

✅ **Ручное подтверждение** перед добавлением документов

## После успешного добавления

После того, как все 20 документов будут добавлены к агенту:

✅ Автоматическая синхронизация через cron будет работать корректно
✅ При изменении файлов в `quarters/` они будут автоматически обновляться в ElevenLabs
✅ Кодировка UTF-8 будет сохраняться

## Troubleshooting

### Проблема: Chrome не найден
```bash
# Установите Chrome:
# https://www.google.com/chrome/
```

### Проблема: WebDriver не работает
```bash
# Переустановите Selenium:
/Users/admin/MM-RAG/venv/bin/pip install --upgrade selenium
```

### Проблема: Скрипт не может найти элементы
- UI ElevenLabs мог измениться
- Попробуйте добавить документы вручную через инструкцию в AGENT_UPDATE_INSTRUCTIONS.md

## Альтернатива

Если Selenium не работает, используйте ручное добавление:
1. Откройте https://elevenlabs.io/app/conversational-ai/agents/agent_8901k4s5hkbkf7gsf1tk5r0a4g8t/edit
2. Найдите раздел Knowledge Base
3. Добавьте документы из списка выше
4. Сохраните изменения

---

**Дата создания**: 20 ноября 2025
**Автор**: Claude Code
**Версия**: 1.0
