# Dockerfile для BIR.BY Auto-Updater
FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание директорий
RUN mkdir -p cache quarters logs

# Права на выполнение скриптов
RUN chmod +x setup_scheduler.sh data_updater.py web_monitor.py

# Настройка cron
RUN touch /var/log/cron.log

# Создание стартового скрипта
RUN echo '#!/bin/bash\n\
# Запуск cron демона\n\
service cron start\n\
\n\
# Добавление задания в cron (каждый час)\n\
echo "0 * * * * cd /app && python3 data_updater.py >> /app/logs/cron.log 2>&1" | crontab -\n\
\n\
# Создание начальной конфигурации\n\
python3 -c "import json; config = {\n\
    '\''check_interval_minutes'\'': 60,\n\
    '\''force_update_hours'\'': 24,\n\
    '\''enable_change_detection'\'': True,\n\
    '\''enable_scheduled_updates'\'': True,\n\
    '\''enable_notifications'\'': True,\n\
    '\''notification_methods'\'': ['\''log'\'', '\''file'\''],\n\
    '\''webhook_url'\'': None\n\
}; json.dump(config, open('\''update_config.json'\'', '\''w'\''), indent=2)"\n\
\n\
# Первичное обновление данных\n\
python3 data_updater.py --force\n\
\n\
# Запуск веб-интерфейса\n\
exec python3 web_monitor.py' > /app/start.sh

RUN chmod +x /app/start.sh

# Экспорт портов
EXPOSE 5000

# Том для данных
VOLUME ["/app/quarters", "/app/cache", "/app/logs"]

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Minsk

# Запуск
CMD ["/app/start.sh"]




