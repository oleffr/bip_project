import os
import sys
import logging
from datetime import datetime
from mail_processor import MailRuProcessor

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spam_check.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Запуск проверки с обработкой ошибок"""
    
    # Получаем данные из переменных окружения
    email = os.environ.get('MAILRU_EMAIL')
    password = os.environ.get('MAILRU_PASSWORD')
    
    if not email or not password:
        logging.error("Не заданы переменные окружения MAILRU_EMAIL или MAILRU_PASSWORD")
        sys.exit(1)
    
    logging.info(f"Запуск проверки почты для {email}")
    
    try:
        processor = MailRuProcessor(email, password)
        processor.process_unread_messages(max_messages=50)
        logging.info("Проверка завершена успешно")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()