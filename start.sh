#!/bin/bash
# Скрипт запуска для Render

echo "Starting Roblox Login Bot..."

# Проверяем наличие переменных окружения
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Warning: TELEGRAM_BOT_TOKEN not set"
fi

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "Warning: TELEGRAM_CHAT_ID not set"
fi

# Запускаем приложение
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 app:app 