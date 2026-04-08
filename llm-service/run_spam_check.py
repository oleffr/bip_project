import os
import sys
import logging
import time
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
    """Запуск проверки почты каждые 15 минут"""
    
    # Получаем данные из переменных окружения
    email = os.environ.get('MAILRU_EMAIL')
    password = os.environ.get('MAILRU_PASSWORD')
    
    if not email or not password:
        logging.error("Не заданы переменные окружения MAILRU_EMAIL или MAILRU_PASSWORD")
        sys.exit(1)
    
    logging.info(f"Запуск периодической проверки почты для {email} (интервал 15 минут)")
    
    processor = MailRuProcessor(email, password)
    
    while True:
        try:
            logging.info(f"Начало цикла проверки: {datetime.now()}")
            processor.process_unread_messages(max_messages=50)
            logging.info(f"Цикл проверки завершён: {datetime.now()}")
        except Exception as e:
            logging.error(f"Ошибка во время проверки: {e}", exc_info=True)
            # Продолжаем работу, не падаем
        
        # Ждём 15 минут (900 секунд) перед следующим запуском
        logging.info("Ожидание 15 минут до следующей проверки...")
        time.sleep(900)

if __name__ == "__main__":
    main()