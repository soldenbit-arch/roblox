# Краткая инструкция по развертыванию на Render

## Быстрый старт

1. **Загрузите код на GitHub**
   ```bash
   git add .
   git commit -m "Initial commit: Roblox Login Bot"
   git push origin main
   ```

2. **Создайте сервис на Render**
   - Зайдите на [render.com](https://render.com)
   - Создайте новый Web Service
   - Подключите ваш GitHub репозиторий

3. **Настройте переменные окружения**
   ```
   TELEGRAM_BOT_TOKEN=ваш_токен_бота
   TELEGRAM_CHAT_ID=ваш_chat_id
   ```

4. **Развертывание**
   - Render автоматически установит зависимости
   - Приложение запустится на `https://your-app-name.onrender.com`

## Проверка работоспособности

После развертывания проверьте:
- `https://your-app-name.onrender.com/health` - статус сервиса
- `https://your-app-name.onrender.com/` - главная страница

## Логи и мониторинг

- Логи доступны в консоли Render
- Все операции логируются в Telegram
- Эндпоинт `/health` для мониторинга

## Обновления

При каждом push в main ветку Render автоматически перезапустит приложение. 