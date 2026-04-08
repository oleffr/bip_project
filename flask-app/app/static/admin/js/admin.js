document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('userCheckForm');
    const resultDiv = document.getElementById('result');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = document.getElementById('username').value.trim();

        // Очищаем предыдущее сообщение и показываем загрузку
        resultDiv.textContent = 'Проверка...';
        resultDiv.className = 'result';

        try {
            // Отправляем запрос к бэкенду
            const response = await fetch('/api/get_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: username })
            });

            // Проверяем статус ответа
            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();

            // Обрабатываем ответ от бэкенда
            if (data.exists) {
                resultDiv.textContent = `Пользователь "${username}" найден!`;
                resultDiv.className = 'result success';
            } else {
                resultDiv.textContent = `Пользователь "${username}" не найден.`;
                resultDiv.className = 'result error';
            }
        } catch (error) {
            console.error('Ошибка при проверке пользователя:', error);
            resultDiv.textContent = 'Ошибка при проверке. Попробуйте снова.';
            resultDiv.className = 'result error';
        }
    });
});
