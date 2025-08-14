document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const resultDiv = document.getElementById('result');
    const codeForm = document.getElementById('codeForm');
    
    let currentSessionId = null;
    
    // Функция для показа сообщения
    function showMessage(message, type = 'info') {
        resultDiv.innerHTML = `<div class="${type}">${message}</div>`;
        resultDiv.className = `result-message ${type}`;
        resultDiv.style.display = 'block';
    }
    
    // Функция для скрытия сообщения
    function hideMessage() {
        resultDiv.style.display = 'none';
    }
    
    // Функция для показа формы 2FA
    function show2FAForm(sessionId) {
        currentSessionId = sessionId;
        loginForm.style.display = 'none';
        codeForm.style.display = 'block';
        showMessage('Введите код двухфакторной аутентификации, отправленный на ваш телефон/email', 'info');
    }
    
    // Функция для возврата к форме логина
    function showLoginForm() {
        currentSessionId = null;
        loginForm.style.display = 'block';
        codeForm.style.display = 'none';
        hideMessage();
    }
    
    // Обработчик формы логина
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember').checked;
        
        if (!username || !password) {
            showMessage('Пожалуйста, заполните все поля', 'error');
            return;
        }
        
        // Показываем загрузку
        const submitButton = loginForm.querySelector('.login-button');
        const originalText = submitButton.querySelector('.button-text').textContent;
        submitButton.querySelector('.button-text').textContent = 'Вход...';
        submitButton.disabled = true;
        
        try {
            showMessage('Подключаюсь к Roblox...', 'info');
            
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    username, 
                    password, 
                    remember 
                })
            });
            
            const data = await response.json();
            
            if (data.need_code) {
                // Требуется 2FA
                show2FAForm(data.session_id);
            } else if (data.success) {
                showMessage(`✅ ${data.message}`, 'success');
                loginForm.reset();
            } else {
                showMessage(`❌ ${data.message}`, 'error');
            }
        } catch (error) {
            showMessage(`❌ Ошибка: ${error.message}`, 'error');
        } finally {
            // Восстанавливаем кнопку
            submitButton.querySelector('.button-text').textContent = originalText;
            submitButton.disabled = false;
        }
    });
    
    // Обработчик формы 2FA
    codeForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const code = document.getElementById('twofaCode').value;
        
        if (!code) {
            showMessage('Пожалуйста, введите код 2FA', 'error');
            return;
        }
        
        if (!currentSessionId) {
            showMessage('Ошибка сессии. Попробуйте войти заново.', 'error');
            showLoginForm();
            return;
        }
        
        // Показываем загрузку
        const submitButton = codeForm.querySelector('.submit-2fa-button');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Проверка...';
        submitButton.disabled = true;
        
        try {
            showMessage('Проверяю код 2FA...', 'info');
            
            const response = await fetch('/submit_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    session_id: currentSessionId,
                    code: code
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showMessage(`✅ ${data.message}`, 'success');
                codeForm.reset();
                setTimeout(() => {
                    showLoginForm();
                }, 3000);
            } else {
                showMessage(`❌ ${data.message}`, 'error');
            }
        } catch (error) {
            showMessage(`❌ Ошибка: ${error.message}`, 'error');
        } finally {
            // Восстанавливаем кнопку
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    });
    
    // Кнопка "Назад" для возврата к форме логина
    const backButton = document.getElementById('backToLogin');
    if (backButton) {
        backButton.addEventListener('click', function(e) {
            e.preventDefault();
            showLoginForm();
        });
    }
    
    // Кнопка тестирования Roblox
    const testButton = document.getElementById('testRoblox');
    if (testButton) {
        testButton.addEventListener('click', async function() {
            try {
                testButton.textContent = 'Тестирую...';
                testButton.disabled = true;
                
                const response = await fetch('/test-roblox');
                const data = await response.json();
                
                if (data.status === 'success') {
                    showMessage(`✅ ${data.message}\nСтатус: ${data.status_code}\nРазмер ответа: ${data.content_length} символов`, 'success');
                } else {
                    showMessage(`❌ ${data.message}`, 'error');
                }
            } catch (error) {
                showMessage(`❌ Ошибка тестирования: ${error.message}`, 'error');
            } finally {
                testButton.textContent = 'Тест подключения к Roblox';
                testButton.disabled = false;
            }
        });
    }
    
    // Автоматическая очистка старых сообщений
    setInterval(() => {
        const messages = document.querySelectorAll('.result-message');
        messages.forEach(message => {
            if (message.classList.contains('success') || message.classList.contains('error')) {
                const timestamp = message.dataset.timestamp || 0;
                if (Date.now() - timestamp > 10000) { // 10 секунд
                    message.style.display = 'none';
                }
            }
        });
    }, 5000);
}); 