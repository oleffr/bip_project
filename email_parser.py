import re
from bs4 import BeautifulSoup

from urllib.parse import urlparse

#-----------------идет для очистики писем-------------


def safe_extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc

        # фильтруем мусор
        if not domain or len(domain) < 3:
            return ""
        if " " in domain:
            return ""

        return domain
    except Exception:
        return ""

def clean_text(text: str) -> str:
    """Убираем base64-артефакты и лишние пробелы"""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ')
    return text.strip()

def extract_from_html(html: str) -> tuple[str, list]:
    """Текст и ссылки из HTML"""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")
    links = [a['href'] for a in soup.find_all('a', href=True)]
    return text, links

def extract_urls(text: str) -> list[str]:
    """ URL из текста"""
    return re.findall(r'https?://[^\s<>"\']+', text)

def normalize_input(x):
    """
    Приводит любой вход к единому формату dict
    """
    if isinstance(x, str):
        return {
            "text": x,
            "html": "",
            "from": "",
            "subject": ""
        }
    elif isinstance(x, dict):
        return {
            "text": x.get("text", ""),
            "html": x.get("html", ""),
            "from": x.get("from", ""),
            "subject": x.get("subject", "")
        }
    else:
        raise ValueError("Unsupported input type")

def extract_features(parsed_email: dict) -> dict:
    text = parsed_email["text"]
    html = parsed_email["html"]

    html_text, html_links = extract_from_html(html)

    full_text = text + "\n" + html_text
    full_text = clean_text(full_text)

    text_urls = extract_urls(text)
    all_urls = list(set(text_urls + html_links))

    domains = []
    for url in all_urls:
        domain = safe_extract_domain(url)
        if domain:
            domains.append(domain)

    return {
        "text": full_text,
        "urls": all_urls,
        "domains": domains,
        "from": parsed_email["from"],
        "subject": parsed_email["subject"]
    }

def preprocess_email(x) -> str:
    parsed = normalize_input(x)

    features = extract_features(parsed)
    return f"""
    {features['text']}
    """

#-----------------идет в mail_processor----------------

def extract_links(text: str) -> list[str]:
    return re.findall(r'https?://[^\s<>"\']+', text)


def parse_email(msg) -> dict:
    # отправитель
    sender = msg.from_ or ""

    # получатели (imap_tools уже даёт список)
    recipients = msg.to or []

    # тема
    subject = msg.subject or ""

    # текст + html
    text = msg.text or ""
    html = msg.html or ""

    # вытаскиваем текст из html
    html_text = ""
    html_links = []

    if html:
        soup = BeautifulSoup(html, "html.parser")
        html_text = soup.get_text(" ")
        html_links = [a['href'] for a in soup.find_all('a', href=True)]

    # объединяем
    full_text = f"{subject}\n{text}\n{html_text}"

    # чистим (твоя функция)
    clean = preprocess_email(full_text)

    # ссылки
    text_links = extract_links(text)
    all_links = list(set(text_links + html_links))

    return {
        "sender": sender,
        "recipients": recipients,
        "subject": subject,
        "text": clean,
        "links": all_links
    }