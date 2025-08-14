#!/usr/bin/env python3
"""
Тестовый файл для проверки работоспособности Roblox Login Bot
"""

import requests
import json
import time

def test_health_endpoint(base_url):
    """Тестирует эндпоинт здоровья"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_main_page(base_url):
    """Тестирует главную страницу"""
    try:
        response = requests.get(base_url, timeout=10)
        print(f"Main page: {response.status_code}")
        if response.status_code == 200:
            print("Main page loaded successfully")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Main page test failed: {e}")
        return False

def test_login_endpoint(base_url):
    """Тестирует эндпоинт входа (без реальных данных)"""
    try:
        test_data = {
            "username": "test_user",
            "password": "test_password",
            "remember": False
        }
        
        response = requests.post(
            f"{base_url}/login",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Login endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Login test failed: {e}")
        return False

def main():
    """Основная функция тестирования"""
    # URL для тестирования (локальный или удаленный)
    base_url = "http://localhost:5000"  # Измените на ваш URL
    
    print("=== Roblox Login Bot Test ===")
    print(f"Testing URL: {base_url}")
    print()
    
    # Тест 1: Проверка здоровья
    print("1. Testing health endpoint...")
    health_ok = test_health_endpoint(base_url)
    print()
    
    # Тест 2: Главная страница
    print("2. Testing main page...")
    main_ok = test_main_page(base_url)
    print()
    
    # Тест 3: Эндпоинт входа
    print("3. Testing login endpoint...")
    login_ok = test_login_endpoint(base_url)
    print()
    
    # Результаты
    print("=== Test Results ===")
    print(f"Health: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Main page: {'✅ PASS' if main_ok else '❌ FAIL'}")
    print(f"Login: {'✅ PASS' if login_ok else '❌ FAIL'}")
    
    if all([health_ok, main_ok, login_ok]):
        print("\n🎉 All tests passed! Application is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 