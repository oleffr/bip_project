document.addEventListener('DOMContentLoaded', function() {
    const tokensList = document.getElementById('tokensList');
    const loader = document.getElementById('tokensLoader');

    // Обработчик для формы выхода
    const logoutForm = document.getElementById('logoutForm');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function(e) {
            // Можно добавить подтверждение выхода
            if (!confirm('Вы уверены, что хотите выйти из админ‑панели?')) {
                e.preventDefault();
                return;
            }
            // Форма будет отправлена на /api/logout согласно атрибутам action и method
        });
    }

    // Функция для загрузки списка токенов
    async function loadTokens() {
        // Показываем загрузчик
        loader.style.display = 'block';
        tokensList.innerHTML = '';

        try {
            const response = await fetch('/api/get_users_tokens', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();

            // Скрываем загрузчик
            loader.style.display = 'none';

            // Проверяем результат
            if (data.result === true && data.tokens && data.tokens.length > 0) {
                // Отображаем список токенов
                tokensList.innerHTML = data.tokens.map(token => `
                    <div class="token-item">
                <span class="token-value">${token}</span>
                <button class="copy-btn" data-token="${token}">Копировать</button>
            </div>
        `).join('');

                // Добавляем обработчики для кнопок копирования
                document.querySelectorAll('.copy-btn').forEach(button => {
                    button.addEventListener('click', handleCopyToken);
                });
            } else {
                // Если токенов нет
                tokensList.innerHTML = '<div class="no-tokens">Токены не найдены</div>';
            }
        } catch (error) {
            console.error('Ошибка при загрузке токенов:', error);
            loader.style.display = 'none';
            tokensList.innerHTML = `
                <div class="error-message">
                    Ошибка загрузки токенов. Проверьте подключение к серверу.
                </div>
            `;
        }
    }

    // Обработчик копирования токена
    function handleCopyToken(e) {
        const token = e.target.getAttribute('data-token');

        navigator.clipboard.writeText(token)
            .then(() => {
                // Визуальная обратная связь
                const originalText = e.target.textContent;
                e.target.textContent = 'Скопировано!';
                setTimeout(() => {
                    e.target.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('Ошибка копирования в буфер:', err);
                alert('Не удалось скопировать токен. Используйте Ctrl+C.');
            });
    }

    // Загружаем токены при загрузке страницы
    loadTokens();
});
