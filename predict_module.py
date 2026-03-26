import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Tuple

# Константы
DEFAULT_MODEL_PATH = "D:\\vas\\БИП\\bip_project\\test_ml\\final_model_test"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_tokenizer = None
_model = None


def load_model(model_path: str = DEFAULT_MODEL_PATH):
    """Загружает токенизатор и модель из указанной директории."""
    global _tokenizer, _model
    if _tokenizer is not None and _model is not None:
        return

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Модель не найдена по пути: {model_path}")

    print(f"Загрузка модели из {model_path}...", file=sys.stderr)
    _tokenizer = AutoTokenizer.from_pretrained(model_path)
    _model = AutoModelForSequenceClassification.from_pretrained(model_path)
    _model.to(DEVICE)
    _model.eval()
    print("Модель успешно загружена.", file=sys.stderr)


def predict(text: str) -> bool:
    """
    Классифицирует один текст
    """
    if _tokenizer is None or _model is None:
        load_model()

    # Токенизация
    inputs = _tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=128,  
        return_tensors="pt"
    ).to(DEVICE)

    # Предсказание
    with torch.no_grad():
        outputs = _model(**inputs)
        logits = outputs.logits
        pred_class = torch.argmax(logits, dim=1).item()

    # Возвращаем True для класса 1 (спам/фишинг)
    return pred_class == 1


def predict_proba(text: str) -> float:
    """
    Возвращает вероятность принадлежности текста к классу спам/фишинг (класс 1).
    """
    if _tokenizer is None or _model is None:
        load_model()

    inputs = _tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=128,
        return_tensors="pt"
    ).to(DEVICE)

    with torch.no_grad():
        outputs = _model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        prob_spam = probs[0, 1].item()

    return prob_spam


def predict_from_file(filepath: str) -> Tuple[bool, float]:
    """
    Читает весь файл как единый текст и возвращает предсказание и вероятность.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    if not content:
        raise ValueError("Файл пуст")
    pred = predict(content)
    prob = predict_proba(content)
    return pred, prob


def test_from_file(filepath: str, output=None):
    """
    Читает файл построчно (каждая строка – отдельный текст) и выводит предсказания.
    """
    if _tokenizer is None or _model is None:
        load_model()

    if output is None:
        output = sys.stdout

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f]

    print(f"Обрабатывается {len(lines)} строк...", file=sys.stderr)

    for i, line in enumerate(lines, 1):
        if not line.strip():
            # пустые строки пропускаем или можно выводить как есть
            continue
        pred = predict(line)
        label = "SPAM" if pred else "OK"
        output.write(f"{label}\t{line}\n")

    print(f"Готово. Результаты записаны.", file=sys.stderr)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Интерфейс для модели обнаружения спама/фишинга.")
    parser.add_argument("--test", type=str, help="Путь к файлу с текстами для тестирования (построчно)")
    parser.add_argument("--file-as-text", type=str, help="Путь к файлу, который будет обработан как одно сообщение")
    parser.add_argument("--text", type=str, help="Одиночный текст для предсказания")
    parser.add_argument("--model_path", type=str, default=DEFAULT_MODEL_PATH, help="Путь к папке с моделью")

    args = parser.parse_args()

    if args.model_path:
        load_model(args.model_path)

    if args.text:
        result = predict(args.text)
        prob = predict_proba(args.text)
        print(f"Текст: {args.text}")
        print(f"Предсказание: {'СПАМ/ФИШИНГ' if result else 'БЕЗОПАСНО'}")
        print(f"Вероятность спама: {prob:.4f}")

    if args.test:
        test_from_file(args.test)

    if args.file_as_text:
        pred, prob = predict_from_file(args.file_as_text)
        print(f"Текст из файла {args.file_as_text}")
        print(f"Предсказание: {'СПАМ/ФИШИНГ' if pred else 'БЕЗОПАСНО'}")
        print(f"Вероятность спама: {prob:.4f}")

    if not args.text and not args.test and not args.file_as_text:
        parser.print_help()