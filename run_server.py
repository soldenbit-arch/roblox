#!/usr/bin/env python3
"""
Скрипт для запуска Flask сервера
"""
import os
import sys
from app import app

if __name__ == '__main__':
    print("🚀 Запуск Flask сервера...")
    print("📍 Сервер будет доступен по адресу: http://localhost:5000")
    print("🧪 Тестовая страница: http://localhost:5000/test")
    print("💚 Страница логина: http://localhost:5000/login.html")
    print("🔍 Проверка состояния: http://localhost:5000/health")
    print("\nДля остановки сервера нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        app.run(
            host='0.0.0.0',  # Доступен извне
            port=5000,        # Порт 5000
            debug=True,       # Режим отладки
            threaded=True     # Многопоточность
        )
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1) 