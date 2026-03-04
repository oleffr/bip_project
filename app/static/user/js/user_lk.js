document.addEventListener('DOMContentLoaded', function() {
    const checkServerBtn = document.getElementById('checkServerBtn');
    const serverStatus = document.getElementById('serverStatus');

    checkServerBtn.addEventListener('click', async function() {
        // Очищаем предыдущее сообщение и показываем загрузку
        serverStatus.textContent = 'Проверка...';
        serverStatus.className = 'status-message';

        try {
            // Отправляем запрос к API для проверки сервера
            const response = await fetch('/api/ping', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }

            const data = await response.json();

            // Обрабатываем ответ от сервера
            if (data.status === 'ok') {
                serverStatus.textContent = 'Сервер доступен! Всё работает нормально.';
                serverStatus.className = 'status-message success';
            } else {
                serverStatus.textContent = 'Сервер ответил, но статус не OK.';
                serverStatus.className = 'status-message error';
            }
        } catch (error) {
            console.error('Ошибка при проверке сервера:', error);
            serverStatus.textContent = 'Ошибка подключения к серверу. Проверьте сеть или сервер.';
            serverStatus.className = 'status-message error';
        }
    });
});
