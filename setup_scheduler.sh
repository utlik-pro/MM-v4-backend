#!/bin/bash

# Скрипт настройки планировщика для автоматического обновления данных BIR.BY

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPDATER_SCRIPT="$SCRIPT_DIR/data_updater.py"
CRON_LOG="$SCRIPT_DIR/cron.log"

echo "🔧 Настройка планировщика автообновления BIR.BY"
echo "📁 Рабочая директория: $SCRIPT_DIR"

# Проверяем наличие Python и необходимых файлов
if [ ! -f "$UPDATER_SCRIPT" ]; then
    echo "❌ Файл data_updater.py не найден!"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен!"
    exit 1
fi

# Делаем скрипт исполняемым
chmod +x "$UPDATER_SCRIPT"

echo "
📅 Варианты настройки планировщика:

1) Каждый час (рекомендуется)
2) Каждые 30 минут (частые обновления)
3) Каждые 6 часов (редкие обновления)
4) Каждый день в 08:00
5) Настроить вручную
6) Запустить демон (постоянная работа)
7) Показать текущие задания cron
8) Удалить задания cron
"

read -p "Выберите вариант (1-8): " choice

case $choice in
    1)
        # Каждый час
        CRON_EXPR="0 * * * *"
        DESCRIPTION="каждый час"
        ;;
    2)
        # Каждые 30 минут
        CRON_EXPR="*/30 * * * *"
        DESCRIPTION="каждые 30 минут"
        ;;
    3)
        # Каждые 6 часов
        CRON_EXPR="0 */6 * * *"
        DESCRIPTION="каждые 6 часов"
        ;;
    4)
        # Каждый день в 08:00
        CRON_EXPR="0 8 * * *"
        DESCRIPTION="каждый день в 08:00"
        ;;
    5)
        # Ручная настройка
        echo "Введите cron выражение (например: '0 */2 * * *' для каждых 2 часов):"
        read -p "Cron выражение: " CRON_EXPR
        DESCRIPTION="по расписанию: $CRON_EXPR"
        ;;
    6)
        # Демон
        echo "🚀 Запуск демона автообновления..."
        cd "$SCRIPT_DIR"
        python3 "$UPDATER_SCRIPT" --daemon
        exit 0
        ;;
    7)
        # Показать текущие задания
        echo "📋 Текущие задания cron для BIR.BY:"
        crontab -l | grep -E "(bir|BIR)" || echo "Заданий не найдено"
        exit 0
        ;;
    8)
        # Удалить задания
        echo "🗑️ Удаление заданий cron для BIR.BY..."
        (crontab -l | grep -v -E "(bir|BIR|data_updater)") | crontab -
        echo "✅ Задания удалены"
        exit 0
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

# Создаем cron задание
CRON_COMMAND="cd $SCRIPT_DIR && python3 $UPDATER_SCRIPT >> $CRON_LOG 2>&1"
CRON_LINE="$CRON_EXPR $CRON_COMMAND"

echo "
📝 Настройка cron задания:
Расписание: $DESCRIPTION
Команда: $CRON_COMMAND
"

read -p "Продолжить? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Отменено"
    exit 0
fi

# Добавляем задание в crontab
(crontab -l 2>/dev/null | grep -v -E "data_updater"; echo "$CRON_LINE") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron задание успешно добавлено!"
    echo "📋 Проверить задания: crontab -l"
    echo "📄 Логи: $CRON_LOG"
    echo "🔍 Статус системы: python3 $UPDATER_SCRIPT --status"
else
    echo "❌ Ошибка добавления cron задания"
    exit 1
fi

# Создаем начальную конфигурацию, если её нет
CONFIG_FILE="$SCRIPT_DIR/update_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "📋 Создание конфигурации по умолчанию..."
    python3 -c "
import json

config = {
    'check_interval_minutes': 60,
    'force_update_hours': 24,
    'enable_change_detection': True,
    'enable_scheduled_updates': True,
    'enable_notifications': True,
    'notification_methods': ['log', 'file'],
    'webhook_url': None,
    'email_settings': {
        'enabled': False,
        'smtp_server': None,
        'smtp_port': 587,
        'username': None,
        'password': None,
        'to_email': None
    }
}

with open('$CONFIG_FILE', 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print('✅ Конфигурация создана: $CONFIG_FILE')
"
fi

echo "
🎉 Настройка завершена!

📚 Полезные команды:
- Проверить статус: python3 $UPDATER_SCRIPT --status
- Принудительное обновление: python3 $UPDATER_SCRIPT --force
- Проверить изменения: python3 $UPDATER_SCRIPT --check
- Показать cron задания: crontab -l
- Просмотр логов: tail -f $CRON_LOG
"




