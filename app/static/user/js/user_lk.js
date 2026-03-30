document.addEventListener('DOMContentLoaded', function() {
    const checkServerBtn = document.getElementById('checkServerBtn');
    const serverStatus = document.getElementById('serverStatus');

    checkServerBtn.addEventListener('click', async function() {
        // Очищаем предыдущее сообщение и показываем загрузку
        serverStatus.textContent = 'Проверка...';
        serverStatus.className = 'status-message';

        try {
            // Отправляем запрос к API для проверки сервера
            const response = await fetch('/api/test', {
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
    // Элементы формы добавления почты
const emailForm = document.getElementById('emailForm');
const emailInput = document.getElementById('emailInput');
const passwordInput = document.getElementById('passwordInput');
const formMessage = document.getElementById('formMessage');
const emailsList = document.getElementById('emailsList');

// Функция для загрузки списка почт
async function loadEmails() {
    try {
        const response = await fetch('/api/emails', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Ошибка загрузки почт: ${response.status}`);
        }

        const emails = await response.json();

        // Обновляем список почт
        if (emails.length > 0) {
            emailsList.innerHTML = emails.map(email => `
                <div class="email-item">
                    <span class="email-address">${email.address}</span>
                    <button class="delete-email-btn" data-email="${email.address}">Удалить</button>
                </div>
            `).join('');

            // Добавляем обработчики для кнопок удаления
            document.querySelectorAll('.delete-email-btn').forEach(button => {
                button.addEventListener('click', handleDeleteEmail);
            });
        } else {
            emailsList.innerHTML = '<p class="empty-message">Почты не добавлены</p>';
        }
    } catch (error) {
        console.error('Ошибка при загрузке списка почт:', error);
        emailsList.innerHTML = '<p class="empty-message">Ошибка загрузки списка почт</p>';
    }
}

// Обработчик отправки формы добавления почты
emailForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    // Очищаем предыдущее сообщение
    formMessage.textContent = '';
    formMessage.className = 'form-message';

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    try {
        const response = await fetch('/api/add-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            throw new Error(`Ошибка добавления почты: ${response.status}`);
        }

        const result = await response.json();

        formMessage.textContent = 'Почта успешно добавлена!';
        formMessage.className = 'form-message success';

        // Очищаем форму
        emailInput.value = '';
        passwordInput.value = '';

        // Перезагружаем список почт
        await loadEmails();
    } catch (error) {
        console.error('Ошибка при добавлении почты:', error);
        formMessage.textContent = 'Ошибка добавления почты. Попробуйте ещё раз.';
        formMessage.className = 'form-message error';
    }
});

// Обработчик удаления почты
async function handleDeleteEmail(e) {
    const email = e.target.getAttribute('data-email');

    if (!confirm(`Вы уверены, что хотите удалить почту "${email}"?`)) {
        return;
    }

    try {
        const response = await fetch('/api/delete-email', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });

        if (!response.ok) {
            throw new Error(`Ошибка удаления почты: ${response.status}`);
        }

        // Показываем сообщение об успехе
        formMessage.textContent = 'Почта удалена!';
        formMessage.className = 'form-message success';

        // Перезагружаем список почт
        await loadEmails();
    } catch (error) {
        console.error('Ошибка при удалении почты:', error);
        formMessage.textContent = 'Ошибка удаления почты. Попробуйте ещё раз.';
        formMessage.className = 'form-message error';
    }
}

// Загружаем список почт при загрузке страницы
loadEmails();


});
