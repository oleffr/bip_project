import email
import base64
import re
import os
import json
from email.header import decode_header
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def clean_email_text(text: str) -> str:
    """Убираем base64-артефакты и лишние пробелы"""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ')
    return text.strip()


def decode_mime_header(header_value: str) -> str:
    """Декодируем MIME-заголовок"""
    if not header_value:
        return ""

    decoded_parts = decode_header(header_value)
    result = []

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or "utf-8", errors="ignore"))
        else:
            result.append(part)

    return "".join(result)


def decode_base64(payload) -> str:
    """Декодируем base64"""
    try:
        return base64.b64decode(payload).decode("utf-8", errors="ignore")
    except Exception:
        return payload


def parse_email(raw_email: str) -> dict[str, str]:
    """Парсим письмо"""
    msg = email.message_from_string(raw_email)

    parsed: dict[str, str] = {
        "subject": decode_mime_header(msg.get("Subject", "")),
        "from": decode_mime_header(msg.get("From", "")),
        "to": decode_mime_header(msg.get("To", "")),
        "text": "",
        "html": ""
    }

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)

            if payload:
                payload = payload.decode(errors="ignore") # type: ignore

            if content_type == "text/plain":
                parsed["text"] += payload or "" # type: ignore
            elif content_type == "text/html":
                parsed["html"] += payload or "" # type: ignore
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            parsed["text"] = payload.decode(errors="ignore") # type: ignore

    return parsed


def extract_from_html(html: str) -> tuple[str, list]:
    """Текст и ссылки из HTML"""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")
    links = [a['href'] for a in soup.find_all('a', href=True)]
    return text, links


def extract_urls(text: str) -> list[str]:
    """ URL из текста"""
    return re.findall(r'https?://\S+', text)


def build_email_features(parsed_email: dict[str, str]) -> dict:
    """Собираем поля письма"""
    text = parsed_email["text"]
    html = parsed_email["html"]

    html_text, html_links = extract_from_html(html)

    full_text = text + "\n" + html_text
    full_text = clean_email_text(full_text)

    text_urls = extract_urls(text)
    all_urls = list(set(text_urls + html_links))

    return {
        "text": full_text,
        "urls": all_urls,
        "from": parsed_email["from"],
        "subject": parsed_email["subject"]
    }


def to_dataset_format(email_features: dict, label = None) -> dict:
    """Сохраняет в датасет только текст"""
    return {
        "text": email_features["text"],
        "label": label
    }


def build_enriched_view(email_features: dict) -> str:
    url_domains = [urlparse(u).netloc for u in email_features["urls"]]

    return f"""
    [FROM] {email_features['from']}
    [SUBJECT] {email_features['subject']}
    [URL_COUNT] {len(email_features['urls'])}
    [URL_DOMAINS] {' '.join(url_domains)}

    [TEXT]
    {email_features['text']}
    """


def process_raw_email(raw_email: str, label=None) -> dict:
    """Обрабатывает сырое письмо"""
    parsed = parse_email(raw_email)
    features = build_email_features(parsed)
    return to_dataset_format(features, label)


def build_dataset_from_folders(
    path_0: str = "emails_0",
    path_1: str = "emails_1",
    output_file: str = "real_emails.json"
) -> None:
    """
    Собирает датасет из папок с письмами.
    
    Args:
        path_0: Путь к папке с письмами класса 0
        path_1: Путь к папке с письмами класса 1
        output_file: Имя выходного JSON-файла
    """
    dataset = []
    
    def process_folder(folder_path: str, label: int) -> None:
        """Обрабатывает одну папку с письмами"""
        if not os.path.exists(folder_path):
            print(f" Папка не найдена: {folder_path}")
            return
            
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            
            if not os.path.isfile(filepath):
                continue
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    raw_email = f.read()
                sample = process_raw_email(raw_email, label)
                dataset.append(sample)
                
            except Exception as e:
                print(f"ERROR: {filepath}: {e}")
    
    # body of build_dataset_from_folders
    for path, label in [(path_0, 0), (path_1, 1)]:
        print(f"Обработка {path}...")
        process_folder(path, label)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"Сохранено {len(dataset)} записей в {output_file}")
    print(f"Класс 0: {sum(1 for item in dataset if item['label'] == 0)}")
    print(f"Класс 1: {sum(1 for item in dataset if item['label'] == 1)}")






if __name__ == "__main__":

    print("=" * 80)
    print("ПРИМЕР: Письмо из emails_0")
    print("=" * 80)
    
    with open("emails_0\\New material_ _Обработка временных рядов_.eml",
              "r", encoding="utf-8") as f:
        raw_email = f.read()
    
    parsed = parse_email(raw_email)
    features = build_email_features(parsed)
    enriched_view = build_enriched_view(features)
    print(enriched_view)
    
    # Также получаем датасет-формат
    sample = to_dataset_format(features, label=0)
    print("\n" + "=" * 50)
    print("ФОРМАТ ДАТАСЕТА (только текст):")
    print("=" * 50)
    print(f"Текст: {sample['text'][:500]}...")  # начало
    print(f"Метка: {sample['label']}")
    


    build_dataset_from_folders(
        path_0="emails_0",
        path_1="emails_1",
        output_file="real_emails.json"
    )