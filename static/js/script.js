document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const resultDiv = document.getElementById('result');
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember').checked;
        
        // Показываем загрузку
        const submitButton = loginForm.querySelector('.login-button');
        const originalText = submitButton.querySelector('.button-text').textContent;
        submitButton.querySelector('.button-text').textContent = 'Вход...';
        submitButton.disabled = true;
        
        try {
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
            
            if (data.success) {
                // Сохраняем данные в localStorage
                localStorage.setItem('username', username);
                localStorage.setItem('loginTime', new Date().toLocaleString('ru-RU'));
                
                // Перенаправляем на страницу успешного входа
                window.location.href = '/final.html';
            }
        } catch (error) {
            resultDiv.innerHTML = `<div class="error">❌ Ошибка: ${error.message}</div>`;
            resultDiv.className = 'result-message error';
            resultDiv.style.display = 'block';
        } finally {
            // Восстанавливаем кнопку
            submitButton.querySelector('.button-text').textContent = originalText;
            submitButton.disabled = false;
        }
    });
}); 