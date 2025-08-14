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
2. **Тестовая страница**: https://roblox-2dyn.onrender.com/test-render
3. **Облачная версия**: https://roblox-2dyn.onrender.com/cloud-test
4. **Проверка состояния**: https://roblox-2dyn.onrender.com/health
5. **Страница логина**: https://roblox-2dyn.onrender.com/login.html

## 🚀 Облачная версия (Без Selenium)

Проект автоматически определяет среду выполнения:

- **Локально**: Использует Selenium + ChromeDriver для полной автоматизации
- **На Render**: Использует HTTP API без Selenium (работает без графического интерфейса)

### Преимущества облачной версии:
- ✅ Работает без ChromeDriver
- ✅ Нет проблем с графическим интерфейсом
- ✅ Автоматическое определение среды
- ✅ Фейковые куки для демонстрации
- ✅ Отправка в Telegram работает
- ✅ CORS настроен для Render

## 🔍 Решение проблем с CORS

### Проблема:
```
Access to XMLHttpRequest at 'https://apis.roblox.com/...' from origin 'https://roblox-2dyn.onrender.com' has been blocked by CORS policy
```

### Решение:
1. **Прокси через наш сервер**: Используйте `/proxy-roblox` маршрут
2. **Правильные CORS заголовки**: Настроены автоматически
3. **Проверка origins**: Только разрешенные домены
4. **Облачная версия**: Автоматически работает без Selenium

## 📁 Структура проекта

```
roblox/
├── app.py                  # Основное Flask приложение
├── wsgi.py                 # WSGI конфигурация для Render
├── run_server.py           # Скрипт для локального запуска
├── requirements.txt        # Python зависимости (с Selenium)
├── requirements-cloud.txt  # Зависимости для облачного хостинга
├── Procfile               # Конфигурация для Render
├── templates/              # HTML шаблоны
│   ├── login.html         # Страница логина
│   ├── test.html          # Тестовая страница
│   └── cloud-test.html    # Тест облачной версии
├── static/                # Статические файлы
├── CORS_SOLUTION.md       # Документация по CORS
├── QUICK_FIX.md           # Быстрое решение CORS
└── CHANGES_SUMMARY.md     # Сводка изменений
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