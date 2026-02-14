import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from transformers import DataCollatorWithPadding
from datasets import Dataset
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import os

print(" НАЧАЛО ПОДГОТОВКИ МОДЕЛИ И ТОКЕНИЗАТОРА")

# Используем абсолютные пути
current_dir = os.getcwd()
results_dir = os.path.join(current_dir, 'results')
final_model_dir = os.path.join(current_dir, 'final_model')

# Создаем директории
os.makedirs(results_dir, exist_ok=True)
os.makedirs(final_model_dir, exist_ok=True)

print(f" Рабочая директория: {current_dir}")

# ЗАГРУЗКА ДАННЫХ
print(" Загрузка данных...")

try:
    train_data = pd.read_csv('sms_split_data/train.csv')
    val_data = pd.read_csv('sms_split_data/validation.csv')
    test_data = pd.read_csv('sms_split_data/test.csv')
    
    X_train = train_data['message']
    y_train = train_data['label_encoded']
    
    X_val = val_data['message']
    y_val = val_data['label_encoded']
    
    X_test = test_data['message']
    y_test = test_data['label_encoded']
    
    print(" Данные успешно загружены из CSV!")
    print(f"   • Обучающая выборка: {len(X_train)} сообщений")
    print(f"   • Валидационная выборка: {len(X_val)} сообщений") 
    print(f"   • Тестовая выборка: {len(X_test)} сообщений")
    
except Exception as e:
    print(f"Ошибка загрузки данных: {e}")
    exit()

# ЗАГРУЗКА ТОКЕНИЗАТОРА
print("\n" + "="*50)
print("ЗАГРУЗКА ТОКЕНИЗАТОРА")
print("="*50)

try:
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    print("Токенизатор успешно загружен!")
except Exception as e:
    print(f"Ошибка загрузки токенизатора: {e}")
    exit()

# ПАРАМЕТРЫ ТОКЕНИЗАЦИИ
tokenization_config = {
    "padding": "max_length",
    "truncation": True,
    "max_length": 128,
    "return_tensors": "pt"
}

print(" Параметры токенизации установлены")

# ФУНКЦИЯ ДЛЯ ТОКЕНИЗАЦИИ
def tokenize_dataset(examples):
    tokenized = tokenizer(
        examples["text"],
        padding=tokenization_config["padding"],
        truncation=tokenization_config["truncation"],
        max_length=tokenization_config["max_length"],
        return_tensors="pt"
    )
    tokenized["labels"] = examples["label"]
    return tokenized

# ПОДГОТОВКА DATASETS
print("\n ПОДГОТОВКА DATASETS:")

train_dict = {"text": X_train.tolist(), "label": y_train.tolist()}
val_dict = {"text": X_val.tolist(), "label": y_val.tolist()}
test_dict = {"text": X_test.tolist(), "label": y_test.tolist()}

train_dataset = Dataset.from_dict(train_dict)
val_dataset = Dataset.from_dict(val_dict)
test_dataset = Dataset.from_dict(test_dict)

# Токенизируем datasets
tokenized_train = train_dataset.map(tokenize_dataset, batched=True, batch_size=16)
tokenized_val = val_dataset.map(tokenize_dataset, batched=True, batch_size=16)
tokenized_test = test_dataset.map(tokenize_dataset, batched=True, batch_size=16)

# Удаляем текстовые колонки
columns_to_remove = ['text']
tokenized_train = tokenized_train.remove_columns(columns_to_remove)
tokenized_val = tokenized_val.remove_columns(columns_to_remove)
tokenized_test = tokenized_test.remove_columns(columns_to_remove)

print(" Datasets подготовлены!")

# ЗАГРУЗКА МОДЕЛИ
print("\n" + "="*50)
print("ЗАГРУЗКА МОДЕЛИ")
print("="*50)

try:
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        num_labels=2,
        ignore_mismatched_sizes=True
    )
    print(" Модель успешно загружена!")
except Exception as e:
    print(f" Ошибка загрузки модели: {e}")
    exit()

# ФУНКЦИЯ ДЛЯ ВЫЧИСЛЕНИЯ МЕТРИК
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    accuracy = accuracy_score(labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='binary')
    return {
        'accuracy': accuracy,
        'precision': precision, 
        'recall': recall, 
        'f1': f1
    }

print(" Функция для вычисления метрик настроена")

# DATA COLLATOR
data_collator = DataCollatorWithPadding(
    tokenizer=tokenizer,
    padding='longest',
    max_length=tokenization_config['max_length'],
    return_tensors="pt"
)

print(" Data Collator создан")

# МИНИМАЛЬНЫЕ ПАРАМЕТРЫ ОБУЧЕНИЯ
print("\n  НАСТРОЙКА ПАРАМЕТРОВ ОБУЧЕНИЯ")

# Пробуем разные комбинации параметров
try:
    # Попытка 1: самые базовые параметры
    training_args = TrainingArguments(
        output_dir=results_dir,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        learning_rate=2e-5,
        save_strategy="no",                           # Не сохраняем чекпоинты во время обучения
        report_to=[],
    )
    print(" Параметры обучения установлены (вариант 1)")
except Exception as e:
    print(f" Ошибка с параметрами вариант 1: {e}")
    try:
        # Попытка 2:  более минимальные параметры
        training_args = TrainingArguments(
            output_dir=results_dir,
            num_train_epochs=3,
            per_device_train_batch_size=8,
            learning_rate=2e-5,
        )
        print(" Параметры обучения установлены (вариант 2)")
    except Exception as e2:
        print(f" Ошибка с параметрами вариант 2: {e2}")
        exit()

# СОЗДАНИЕ TRAINER
print("\n СОЗДАНИЕ TRAINER:")
try:
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
    print(" Trainer создан!")
except Exception as e:
    print(f" Ошибка создания Trainer: {e}")
    exit()

# ЗАПУСК ОБУЧЕНИЯ
print("\n" + "="*50)
print(" ЗАПУСК ОБУЧЕНИЯ")
print("="*50)

try:
    print(" Начало обучения...")
    train_result = trainer.train()
    print(" Обучение завершено успешно!")
    
    # Сохранение модели
    print(" Сохранение модели...")
    model.save_pretrained(final_model_dir)
    tokenizer.save_pretrained(final_model_dir)
    print(f" Модель сохранена в '{final_model_dir}'")
    
    # Оценка на тестовых данных
    print("\n ОЦЕНКА НА ТЕСТОВЫХ ДАННЫХ...")
    test_results = trainer.predict(tokenized_test)
    
    print(" РЕЗУЛЬТАТЫ НА ТЕСТЕ:")
    for metric, value in test_results.metrics.items():
        print(f"   {metric}: {value:.4f}")
        
except Exception as e:
    print(f" Ошибка во время обучения: {e}")
    import traceback
    traceback.print_exc()

print("\n ПРОГРАММА ЗАВЕРШЕНА!")