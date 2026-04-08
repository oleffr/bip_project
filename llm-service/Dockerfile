FROM python:3.11-slim

WORKDIR /app

# Копируем папку со скачанными пакетами
COPY packages /packages

# Копируем requirements.txt (со всеми версиями)
COPY requirements.txt .

# Устанавливаем все зависимости из локальной папки (без интернета)
RUN pip install --no-cache-dir --no-index --find-links /packages -r requirements.txt

# Копируем код приложения
COPY . .

# Убедитесь, что точка входа — правильный файл (run_spam_check.py или другой)
CMD ["python", "run_spam_check.py"]
