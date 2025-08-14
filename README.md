# Roblox Project

## 🚀 Развертывание на Render

Проект автоматически развертывается на Render при пуше в GitHub.

### Ссылки:
- **Продакшн**: https://roblox-2dyn.onrender.com
- **GitHub**: [ссылка на репозиторий]

## 🔧 Локальная разработка

### Установка зависимостей:
```bash
pip install -r requirements.txt
```

### Запуск сервера:
```bash
# Вариант 1: Через Python
python run_server.py

# Вариант 2: Через Flask
python -m flask run --host=0.0.0.0 --port=5000

# Вариант 3: Через Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## 🌐 CORS настройки

Проект настроен для работы как локально, так и на Render:

### Разрешенные origins:
- `https://roblox-2dyn.onrender.com` (продакшн)
- `http://localhost:5000` (локальная разработка)
- `http://localhost:3000` (альтернативный порт)
- `http://127.0.0.1:5000` (альтернативный адрес)

## 🧪 Тестирование

### Локально:
1. **Главная страница**: http://localhost:5000
2. **Тестовая страница**: http://localhost:5000/test
3. **Проверка состояния**: http://localhost:5000/health
4. **Страница логина**: http://localhost:5000/login.html

### На Render:
1. **Главная страница**: https://roblox-2dyn.onrender.com
2. **Тестовая страница**: https://roblox-2dyn.onrender.com/test
3. **Проверка состояния**: https://roblox-2dyn.onrender.com/health
4. **Страница логина**: https://roblox-2dyn.onrender.com/login.html

## 🔍 Решение проблем с CORS

### Проблема:
```
Access to XMLHttpRequest at 'https://apis.roblox.com/...' from origin 'https://roblox-2dyn.onrender.com' has been blocked by CORS policy
```

### Решение:
1. **Прокси через наш сервер**: Используйте `/proxy-roblox` маршрут
2. **Правильные CORS заголовки**: Настроены автоматически
3. **Проверка origins**: Только разрешенные домены

## 📁 Структура проекта

```
roblox/
├── app.py              # Основное Flask приложение
├── wsgi.py             # WSGI конфигурация для Render
├── run_server.py       # Скрипт для локального запуска
├── requirements.txt    # Python зависимости
├── Procfile           # Конфигурация для Render
├── templates/          # HTML шаблоны
│   ├── login.html     # Страница логина
│   └── test.html      # Тестовая страница
├── static/            # Статические файлы
└── CORS_SOLUTION.md   # Документация по CORS
```

## 🚨 Важные замечания

1. **CORS**: Настроен автоматически для всех разрешенных origins
2. **Прокси**: Для Roblox API используйте `/proxy-roblox` маршрут
3. **Безопасность**: В продакшне настройте более строгие CORS правила
4. **Логирование**: Все ошибки логируются на сервере

## 🔄 Обновление на Render

При каждом пуше в GitHub:
1. Render автоматически получает изменения
2. Пересобирает проект
3. Перезапускает сервер
4. Обновляет CORS настройки

## 📞 Поддержка

При возникновении проблем:
1. Проверьте `/health` endpoint
2. Посмотрите логи Render
3. Проверьте консоль браузера
4. Убедитесь, что все зависимости установлены 