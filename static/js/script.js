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
                resultDiv.innerHTML = `
                    <div class="success">
                        ✅ ${data.message}
                        <div class="cookies-display">
                            <strong>Сохраненные куки:</strong><br>
                            <pre>${JSON.stringify(data.cookies, null, 2)}</pre>
                        </div>
                    </div>
                `;
                resultDiv.className = 'result-message success';
                resultDiv.style.display = 'block';
                
                // Очищаем форму
                loginForm.reset();
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