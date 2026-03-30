document.addEventListener('DOMContentLoaded', function() {
    // Элементы интерфейса
    const testApiBtn = document.getElementById('testApiBtn');
    const apiStatus = document.getElementById('apiStatus');

    // Обработчик для кнопки «Проверить API»
    if (testApiBtn) {
        testApiBtn.addEventListener('click', async function() {
            apiStatus.textContent = 'Проверка API...';
            apiStatus.className = 'status-message loading';

            try {
                const response = await fetch('/api/test', {
                    method: 'GET'
                });

                if (!response.ok) {
                    throw new Error(`Ошибка сервера: ${response.status}`);
                }

                const data = await response.json();

                if (data.success) {
                    apiStatus.textContent = 'API работает корректно!';
                    apiStatus.className = 'status-message success';
                } else {
                    apiStatus.textContent = 'API вернул ошибку: ' + (data.message || 'Неизвестная ошибка');
                    apiStatus.className = 'status-message error';
                }
            } catch (error) {
                console.error('Ошибка при проверке API:', error);
                apiStatus.textContent = 'Ошибка подключения к API. Проверьте сервер.';
                apiStatus.className = 'status-message error';
            }
        });
    }

    // Дополнительная функциональность для кнопок авторизации (опционально)
    const loginBtn = document.querySelector('.auth-btn.login-btn');
    const registerBtn = document.querySelector('.auth-btn.register-btn');

    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            console.log('Пользователь нажал кнопку "Вход"');
            // Здесь можно добавить дополнительные действия перед переходом
            // Например: логирование в аналитику, показ загрузчика и т. д.
        });
    }

    if (registerBtn) {
        registerBtn.addEventListener('click', function(e) {
            console.log('Пользователь нажал кнопку "Регистрация"');
            // Аналогично — дополнительные действия перед переходом
        });
    }
});
