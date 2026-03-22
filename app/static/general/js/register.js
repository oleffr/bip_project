document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const registerStatus = document.getElementById('registerStatus');
    let requestTimeout;

    // Вспомогательная функция для показа сообщений
    function showMessage(message, type) {
        registerStatus.textContent = message;
        registerStatus.className = `status-message ${type}`;
    }

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();
        const confirmPassword = document.getElementById('confirmPassword').value.trim();

        // Валидация на клиенте
        if (password !== confirmPassword) {
            showMessage('Пароли не совпадают!', 'error');
            return;
        }

        if (password.length < 6) {
            showMessage('Пароль должен содержать минимум 6 символов!', 'error');
            return;
        }

        if (!email.includes('@')) {
            showMessage('Введите корректный email-адрес!', 'error');
            return;
        }

        // Очищаем предыдущее сообщение и показываем загрузку
        showMessage('Регистрация...', 'loading');

        // Блокируем кнопку на время запроса
        const submitBtn = registerForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;

        // Устанавливаем таймаут
        requestTimeout = setTimeout(() => {
            showMessage('Превышено время ожидания ответа от сервера. Попробуйте ещё раз.', 'error');
            submitBtn.disabled = false;
        }, 10000);

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
            password: password
                })
            });

            // Отменяем таймаут, если запрос завершился раньше
            clearTimeout(requestTimeout);

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();

            // Обрабатываем ответ от сервера
            if (data.success) {
                showMessage('Регистрация успешна! Перенаправление...', 'success');
                // Получаем URL для перенаправления из ответа бэкенда
                const redirectUrl = data.redirect_url;
                // Перенаправляем через 1.5 секунды
                setTimeout(() => {
                    window.location.href = redirectUrl;
                }, 150);
            } else {
                showMessage(data.message || 'Ошибка регистрации', 'error');
                submitBtn.disabled = false; // Разблокируем кнопку при ошибке
            }
        } catch (error) {
            console.error('Ошибка при регистрации:', error);
            // Проверяем, не сработал ли уже таймаут
            if (!registerStatus.textContent.includes('Превышено время ожидания')) {
                showMessage('Ошибка подключения. Проверьте интернет или сервер.', 'error');
            }
            submitBtn.disabled = false; // Разблокируем кнопку в любом случае ошибки
        }
    });
});
