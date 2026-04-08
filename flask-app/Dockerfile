# Используем официальный легковесный образ Python
FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

# Указываем порт, который будет слушать приложение
EXPOSE 5000

# Запускаем приложение напрямую через python (не через flask run)
# Так как у тебя кастомный запуск через класс App
CMD ["python", "run.py"]
