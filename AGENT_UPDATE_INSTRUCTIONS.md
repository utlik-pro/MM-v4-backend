# Инструкция по обновлению агента ElevenLabs

## Проблема
API ElevenLabs не может программно обновить агента с 20 документами - сервер разрывает соединение.

## Решение
Необходимо обновить агента через веб-интерфейс.

## Шаги

### 1. Откройте настройки агента
Перейдите по ссылке:
https://elevenlabs.io/app/conversational-ai/agents/agent_8901k4s5hkbkf7gsf1tk5r0a4g8t/edit

### 2. Найдите раздел "Knowledge Base"
В настройках агента найдите раздел Knowledge Base

### 3. Удалите старые кварталы
Удалите все старые документы кварталов (если есть)

### 4. Добавьте новые документы

#### 18 кварталов с правильной кодировкой:

1. **19-Yuzhnaya-Evropa** (ID: qXtJqqEp0ZkcmJX4gc6v)
2. **26-Afrika** (ID: YKvNKCYwODU8AwJI7Muc)
3. **21-Zapadnyy** (ID: wKmcKNykVwd3TFIxmQdc)
4. **10-Tropicheskie-ostrova** (ID: DLY9LrhEzIzQzGsDOYlC)
5. **30-Severnaya-Amerika** (ID: UmvXAJUR6N8jFbIQIU9o)
6. **27-Happy-Planet** (ID: LBIOsPT66B1gdKbHGv2R)
7. **20-Mirovyh-tantsev** (ID: be45mka7XvHxmtbaOKDR)
8. **29-Severnaya-Evropa** (ID: Nn84sS7X6Piy9Z1UtTdw)
9. **7-Sredizemnomorskiy** (ID: e4V9Igwsug2omLaivTBc)
10. **12-Zapadnaya-Evropa** (ID: fr3uFF45uBR5uIKDx5aP)
11. **18-Chempionov** (ID: VJKupwQM3Ly22RMZj8kO)
12. **9-Yuzhnaya-Amerika** (ID: sYnqGkVVXN6U7ScbsP8N)
13. **22-Tsentralnaya-Evropa** (ID: ebURL7MgqknbKVxkY995)
14. **25-Aziya** (ID: MQH2CsUQj6IHJAgEiSd3)
15. **16-Rodnaya-strana** (ID: NYwYJ0wvDeSLj0BMZJOy)
16. **02-Emirats** (ID: qWSLSMQhjJggi9vmOe5Q)
17. **23-Evraziya** (ID: G9f2bpyZmIEpUPI6EVrx)
18. **11-Avstraliya-i-Okeaniya** (ID: e7XBCzszhGnL4s0eaKmg)

#### 2 общих файла:

19. **04-baza-znaniy-dlya-konsultaciy** (ID: kL3zNCHbhtptIq25QNPm)
20. **00-obschie-svedeniya** (ID: rQciMWgeCGRKhgheCzuJ)

### 5. Сохраните изменения

После добавления всех 20 документов, сохраните настройки агента.

## Проверка

После сохранения проверьте, что все документы отображаются в разделе Knowledge Base агента.

## Альтернатива - попытка через web UI automation

Если вы предпочитаете автоматизацию, можно использовать Selenium или Playwright для автоматического добавления документов через веб-интерфейс. Но это требует дополнительной настройки.

---

**Дата создания**: 20 ноября 2025
**Файл**: AGENT_UPDATE_INSTRUCTIONS.md
