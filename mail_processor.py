import logging
import os
import sys
from imap_tools import MailBox, AND, A
from typing import Optional, List
from email.utils import parsedate_to_datetime
from imap_tools import MailBox, AND
from typing import Optional
from dotenv import load_dotenv
load_dotenv()


# Подключаем модуль классификации
try:
    from predict_module import predict_with_threshold
    from email_parser import parse_email
    from wb_lists import analyze_urls
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    from predict_module import predict_with_threshold
    from email_parser import parse_email
    from wb_lists import analyze_urls

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mail_processor.log'),
        logging.StreamHandler()
    ]
)

class MailRuProcessor:
    """Обработчик почты Mail.ru с использованием imap-tools"""

    def __init__(self, email: str, password: str,
                 imap_server: str = 'imap.mail.ru',
                 imap_port: int = 993):
        self.email = email
        self.password = password
        self.server = imap_server
        self.port = imap_port
        self.mailbox: Optional[MailBox] = None
        self.spam_folder: Optional[str] = None
        self.threshold = 0.9995
        self.temperature = 1

    def connect(self) -> bool:
        """Устанавливает соединение с почтовым сервером"""
        try:
            self.mailbox = MailBox(self.server, self.port)
            self.mailbox.login(self.email, self.password)
            logging.info(f"Успешное подключение к {self.email}")
            return True
        except Exception as e:
            logging.error(f"Ошибка подключения: {e}")
            return False

    def disconnect(self):
        """Закрывает соединение"""
        if self.mailbox:
            self.mailbox.logout()

    def find_spam_folder(self) -> Optional[str]:
        """
        Определяет имя папки спама.
        Сначала ищет папку с флагом \Junk или \Spam, затем по ключевым словам.
        """
        if not self.mailbox:
            return None

        folders = self.mailbox.folder.list()
        for folder in folders:
            if '\\Junk' in folder.flags or '\\Spam' in folder.flags:
                self.spam_folder = folder.name
                logging.info(f"Папка спама найдена по флагу: {self.spam_folder}")
                return self.spam_folder

        # Если не нашли по флагу, ищем по имени
        candidates = ['Спам', 'Spam', 'Junk', 'SPAM']
        for name in candidates:
            try:
                self.mailbox.folder.set(name)
                self.spam_folder = name
                logging.info(f"Папка спама найдена по имени: {self.spam_folder}")
                return self.spam_folder
            except:
                continue

        logging.error("Не удалось определить папку спама")
        return None

    def get_message_text(self, msg) -> str:
        """
        Извлекает текст письма из объекта сообщения imap_tools.
        Объединяет plain и html части.
        """
        text_parts = []
        if msg.text:
            text_parts.append(msg.text)
        if msg.html:
            text_parts.append(msg.html)
        return "\n".join(text_parts)

    def process_unread_messages(self, max_messages: int = 50):
        """Обрабатывает непрочитанные письма"""
        if not self.mailbox and not self.connect():
            return

        # Определяем папку спама, если ещё не определена
        if self.spam_folder is None:
            self.find_spam_folder()

        # Выбираем папку "Входящие"
        self.mailbox.folder.set('INBOX')

        # Поиск непрочитанных писем
        messages = list(self.mailbox.fetch(AND(seen=False), limit=max_messages))
        if not messages:
            logging.info("Непрочитанных писем нет")
            return

        logging.info(f"Найдено непрочитанных писем: {len(messages)}")



        for msg in messages:
            try:

                
                # Собираем полный текст письма (тема + тело)
                parsed = parse_email(msg)

                logging.info(f"SENDER: {parsed['sender']}")
                logging.info(f"RECIPIENTS: {parsed['recipients']}")
                logging.info(f"SUBJECT: {parsed['subject']}")
                logging.info(f"LINKS: {parsed['links'][:3]}")

                full_text = parsed["text"]
                # Получаем предсказание модели
                is_spam, probability = predict_with_threshold(
                        full_text,
                        threshold=self.threshold,
                        temperature=self.temperature
                    )

                logging.info(f"Письмо: {parsed['subject'][:50]}... | Спам: {is_spam} | Вероятность: {probability:.4f}")
                if probability > 0.999:
                    logging.warning(f"СЛИШКОМ УВЕРЕННО: {probability}")
                
                url_analysis = analyze_urls(parsed["links"])
                is_phishing = url_analysis["phishing"]
                # logging.info(f"Is_phishing: {is_phishing}, details {url_analysis['details']}")
                final_spam = is_spam or is_phishing

                if final_spam and self.spam_folder:
                    # Перемещаем в спам
                    self.mailbox.move(msg.uid, self.spam_folder)
                    logging.info(f"Письмо (UID: {msg.uid}) перемещено в папку {self.spam_folder}")
                elif final_spam and not self.spam_folder:
                    # Если папка спама не найдена, хотя бы помечаем флагом
                    self.mailbox.flag(msg.uid, '\\Flagged', True)
                    logging.warning(f"Папка спама не найдена, письмо помечено флагом")
                else:
                    pass

            except Exception as e:
                logging.error(f"Ошибка при обработке письма UID {msg.uid}: {e}")
                continue

        logging.info("Обработка завершена")


def main():
    """Запуск обработчика (использует переменные окружения)"""
    email = os.environ.get('MAILRU_EMAIL')
    password = os.environ.get('MAILRU_PASSWORD')

    if not email or not password:
        logging.error("Не заданы переменные окружения MAILRU_EMAIL или MAILRU_PASSWORD")
        sys.exit(1)

    processor = MailRuProcessor(email, password)
    processor.process_unread_messages(max_messages=50)


if __name__ == "__main__":
    main()