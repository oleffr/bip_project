document.addEventListener('DOMContentLoaded', function() {
    const countdownElement = document.getElementById('countdown');
    const progressBar = document.querySelector('.progress');
    let seconds = 5;

    // Обновляем счётчик и прогресс‑бар каждую секунду
    const timer = setInterval(function() {
        seconds--;
        countdownElement.textContent = seconds;

        // Обновляем ширину прогресс‑бара
        const progressWidth = (seconds / 5) * 100;
        progressBar.style.width = progressWidth + '%';

        // Если время вышло — редирект
        if (seconds <= 0) {
            clearInterval(timer);
            window.location.href = '/';
        }
    }, 1000);

    // Обработчик для кнопки «Перейти на главную сейчас»
    document.querySelector('.home-link').addEventListener('click', function(e) {
        e.preventDefault();
        clearInterval(timer); // Останавливаем таймер
        window.location.href = '/'; // Редирект на главную страницу
    });

    // Дополнительная защита: если по какой‑то причине таймер не сработал
    setTimeout(function() {
        window.location.href = '/';
    }, 6000); // Через 6 секунд принудительный редирект (на 1 секунду позже ожидаемого)
});
