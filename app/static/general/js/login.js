document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginStatus = document.getElementById('loginStatus');
    let requestTimeout; // Для отслеживания таймаута запроса

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        // Очищаем предыдущее сообщение и показываем загрузку
        loginStatus.textContent = 'Выполняется вход...';
        loginStatus.className = 'status-message';

        // Блокируем кнопку на время запроса
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;

        // Устанавливаем таймаут: если за 10 секунд нет ответа — считаем, что ошибка
        requestTimeout = setTimeout(() => {
            loginStatus.textContent = 'Превышено время ожидания ответа от сервера. Попробуйте ещё раз.';
            loginStatus.className = 'status-message error';
            submitBtn.disabled = false; // Разблокируем кнопку
        }, 10000);

        try {
            // Отправляем запрос к API для авторизации
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
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
                loginStatus.textContent = 'Успешный вход! Перенаправление...';
                loginStatus.className = 'status-message success';

                // Получаем URL для перенаправления из ответа бэкенда
                const redirectUrl = data.redirect_url;

                // Выполняем перенаправление через 1.5 секунды
                setTimeout(() => {
                    window.location.href = redirectUrl;
                }, 150);
            } else {
                loginStatus.textContent = data.message || 'Неверные логин или пароль';
                loginStatus.className = 'status-message error';
                submitBtn.disabled = false; // Разблокируем кнопку при ошибке авторизации
            }
        } catch (error) {
            console.error('Ошибка при входе:', error);
            // Таймаут уже мог сработать — проверяем, не установлен ли статус
            if (!loginStatus.textContent.includes('Превышено время ожидания')) {
                loginStatus.textContent = 'Ошибка подключения. Проверьте интернет или сервер.';
                loginStatus.className = 'status-message error';
            }
            submitBtn.disabled = false; // Разблокируем кнопку в любом случае ошибки
        }
    });

});
