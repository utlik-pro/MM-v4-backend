#!/bin/bash
# Скрипт для выполнения одноразового обновления через cron

# Путь к директории проекта
PROJECT_DIR="/Users/admin/MM-RAG"

# Файл для логов
LOG_FILE="$PROJECT_DIR/cron-update.log"

# Переходим в директорию проекта
cd "$PROJECT_DIR"

# Добавляем запись в лог
echo "===========================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Запуск обновления через cron" >> "$LOG_FILE"

# Активируем виртуальное окружение и выполняем обновление
source "$PROJECT_DIR/venv/bin/activate"

# Обновление данных с bir.by + автоматическая загрузка в ElevenLabs
python3 sync-with-monitoring.py --check --upload-to-elevenlabs >> "$LOG_FILE" 2>&1

# Проверяем статус выполнения
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Обновление выполнено успешно" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Ошибка при обновлении" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"