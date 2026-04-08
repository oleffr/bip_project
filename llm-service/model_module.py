import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
    roc_curve,
    auc,
)
from sklearn.model_selection import train_test_split
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)
from datasets import load_dataset, Dataset

# ----------------------------- Конфигурация ---------------------------------
RANDOM_SEED = 42
TEST_SIZE = 0.15
VAL_SIZE = 0.15
MAX_LENGTH = 128
TRAIN_BATCH_SIZE = 8
EVAL_BATCH_SIZE = 8
LEARNING_RATE = 2e-5
EPOCHS = 3
MODEL_NAME = "bert-base-uncased"
OUTPUT_DIR = "./results"
FINAL_MODEL_DIR = "./final_model"
DATASET_NAME = "ealvaradob/phishing-dataset"
CONFIG_NAME = "combined_reduced"

# Создание необходимых директорий
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FINAL_MODEL_DIR, exist_ok=True)

np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)

# ----------------------------- Загрузка датасета ----------------------------
print("=" * 60)
print("ЗАГРУЗКА ДАТАСЕТА")
print("=" * 60)

# Загружаем датасет с HuggingFace
dataset = load_dataset(DATASET_NAME, CONFIG_NAME, trust_remote_code=True)
print("Датасет загружен. Структура:")
print(dataset)

if "train" in dataset:
    # У датасета есть разделение train/test
    train_data = dataset["train"]
    if "test" in dataset:
        test_data = dataset["test"]
    else:
        test_data = None
else:
    train_data = dataset
    test_data = None

# Преобразуем в pandas для удобства анализа и разделения
if isinstance(train_data, Dataset):
    train_df = train_data.to_pandas()
else:
    train_df = train_data

if test_data is not None and isinstance(test_data, Dataset):
    test_df = test_data.to_pandas()
else:
    test_df = None

if test_df is None:
    print("Датасет не содержит тестовой выборки. Выполняем разделение самостоятельно.")
    text_col = "text" if "text" in train_df.columns else train_df.columns[0]
    label_col = "label" if "label" in train_df.columns else train_df.columns[1]
    print(f"Используем колонку текста: '{text_col}', метки: '{label_col}'")

    train_df = train_df.rename(columns={text_col: "message", label_col: "label"})

    temp_df, test_df = train_test_split(
        train_df,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=train_df["label"],
    )

    val_ratio = VAL_SIZE / (1 - TEST_SIZE)
    train_df, val_df = train_test_split(
        temp_df,
        test_size=val_ratio,
        random_state=RANDOM_SEED,
        stratify=temp_df["label"],
    )
    print(f"Размеры выборок: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")
else:
   
    text_col = "text" if "text" in train_df.columns else train_df.columns[0]
    label_col = "label" if "label" in train_df.columns else train_df.columns[1]
    train_df = train_df.rename(columns={text_col: "message", label_col: "label"})
    test_df = test_df.rename(columns={text_col: "message", label_col: "label"})

    train_df, val_df = train_test_split(
        train_df,
        test_size=VAL_SIZE,
        random_state=RANDOM_SEED,
        stratify=train_df["label"],
    )
    print(f"Исходный train разбит: train={len(train_df)}, val={len(val_df)}")
    print(f"Тест: {len(test_df)}")

# Вывод распределения классов
for name, df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
    spam_ratio = df["label"].mean() * 100
    print(f"{name}: всего {len(df)}, спам/фишинг: {df['label'].sum()} ({spam_ratio:.1f}%)")

# ----------------------------- Токенизация ----------------------------------
print("\n" + "=" * 60)
print("ЗАГРУЗКА ТОКЕНИЗАТОРА И ТОКЕНИЗАЦИЯ")
print("=" * 60)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

def tokenize_function(examples):
    """Токенизирует тексты и добавляет метки."""
    tokenized = tokenizer(
        examples["message"],
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="pt",
    )
    tokenized["labels"] = examples["label"]
    return tokenized

# Создаем объекты Dataset из pandas DataFrame
train_dataset = Dataset.from_pandas(train_df[["message", "label"]])
val_dataset = Dataset.from_pandas(val_df[["message", "label"]])
test_dataset = Dataset.from_pandas(test_df[["message", "label"]])

# Токенизация с удалением исходного текста
tokenized_train = train_dataset.map(tokenize_function, batched=True, batch_size=16)
tokenized_val = val_dataset.map(tokenize_function, batched=True, batch_size=16)
tokenized_test = test_dataset.map(tokenize_function, batched=True, batch_size=16)

tokenized_train = tokenized_train.remove_columns(["message"])
tokenized_val = tokenized_val.remove_columns(["message"])
tokenized_test = tokenized_test.remove_columns(["message"])

print("Токенизация завершена.")

# ----------------------------- Загрузка модели ------------------------------
print("\n" + "=" * 60)
print("ЗАГРУЗКА МОДЕЛИ BERT")
print("=" * 60)

num_labels = len(train_df["label"].unique())
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=num_labels,
    ignore_mismatched_sizes=True,
)
print(f"Модель загружена. Количество классов: {num_labels}")

# ----------------------------- Метрики --------------------------------------
def compute_metrics(eval_pred):
    """Вычисляет accuracy, precision, recall, f1."""
    predictions, labels = eval_pred
    preds = np.argmax(predictions, axis=1)
    accuracy = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="binary" if num_labels == 2 else "weighted"
    )
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

# ----------------------------- Data Collator --------------------------------
data_collator = DataCollatorWithPadding(
    tokenizer=tokenizer,
    padding="longest",
    max_length=MAX_LENGTH,
    return_tensors="pt",
)

# ----------------------------- Параметры обучения ---------------------------
import transformers
from packaging import version

print(f"Используется transformers версии: {transformers.__version__}")

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=TRAIN_BATCH_SIZE,
    per_device_eval_batch_size=EVAL_BATCH_SIZE,
    learning_rate=LEARNING_RATE,
    eval_strategy="epoch", 
    save_strategy="no",
    report_to=[],
    seed=RANDOM_SEED,
)

# ----------------------------- Создание Trainer -----------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    processing_class=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

# ----------------------------- Обучение -------------------------------------
print("\n" + "=" * 60)
print("ОБУЧЕНИЕ МОДЕЛИ")
print("=" * 60)

try:
    trainer.train()
    print("Обучение завершено успешно!")
except Exception as e:
    print(f"Ошибка во время обучения: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Сохранение модели и токенизатора
model.save_pretrained(FINAL_MODEL_DIR)
tokenizer.save_pretrained(FINAL_MODEL_DIR)
print(f"Модель сохранена в {FINAL_MODEL_DIR}")

# ----------------------------- Оценка на тесте ------------------------------
print("\n" + "=" * 60)
print("ОЦЕНКА НА ТЕСТОВЫХ ДАННЫХ")
print("=" * 60)

test_results = trainer.predict(tokenized_test)
print("Метрики на тесте:")
for key, value in test_results.metrics.items():
    print(f"  {key}: {value:.4f}")

y_true = test_results.label_ids
y_pred = np.argmax(test_results.predictions, axis=1)
# Вероятности для ROC
if num_labels == 2:
    y_scores = torch.softmax(torch.tensor(test_results.predictions), dim=1).numpy()[:, 1]
else:
    y_scores = None

# ----------------------------- Матрица ошибок -------------------------------
def plot_confusion_matrix(y_true, y_pred, labels=None):
    """Строит и отображает матрицу ошибок."""
    cm = confusion_matrix(y_true, y_pred)
    if labels is None:
        labels = ["Безопасно", "Фишинг/Спам"] if num_labels == 2 else [str(i) for i in range(num_labels)]

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels,
                cbar_kws={"label": "Количество"})
    plt.title("Матрица ошибок", fontsize=16, fontweight="bold")
    plt.ylabel("Реальные метки", fontsize=14)
    plt.xlabel("Предсказанные метки", fontsize=14)
    plt.tight_layout()
    plt.show()
    return cm

print("\nПостроение матрицы ошибок...")
cm = plot_confusion_matrix(y_true, y_pred)
tn, fp, fn, tp = cm.ravel() if num_labels == 2 else (None, None, None, None)

# Вывод подробных метрик
print("\nДетальный отчёт классификации:")
print(classification_report(y_true, y_pred, target_names=["Безопасно", "Фишинг/Спам"] if num_labels == 2 else None))

if num_labels == 2:
    print("\nАнализ ошибок:")
    print(f"  True Negative (TN): {tn} - правильно распознанные безопасные сообщения")
    print(f"  False Positive (FP): {fp} - безопасные, ошибочно помеченные как фишинг")
    print(f"  False Negative (FN): {fn} - фишинг, пропущенный фильтром")
    print(f"  True Positive (TP): {tp} - правильно распознанный фишинг")

    # Интерпретация
    if fp > fn:
        print(" Модель СЛИШКОМ АГРЕССИВНА: много ложных срабатываний.")
    elif fn > fp:
        print(" Модель СЛИШКОМ МЯГКАЯ: пропускает много фишинга.")
    else:
        print(" Модель ХОРОШО СБАЛАНСИРОВАНА.")

# ----------------------------- ROC-кривая (для бинарной классификации) -----
def plot_roc_curve(y_true, y_scores):
    """Строит ROC-кривую и вычисляет AUC."""
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC (AUC = {roc_auc:.4f})")
    plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--", label="Случайный")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate (Доля ложных срабатываний)", fontsize=14)
    plt.ylabel("True Positive Rate (Полнота)", fontsize=14)
    plt.title("ROC-кривая", fontsize=16, fontweight="bold")
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()
    return roc_auc

if num_labels == 2 and y_scores is not None:
    print("\nПостроение ROC-кривой...")
    roc_auc = plot_roc_curve(y_true, y_scores)
    print(f"AUC = {roc_auc:.4f}")

# ----------------------------- Анализ ошибок (примеры) ----------------------
def analyze_errors(texts, y_true, y_pred, num_examples=5):
    """Выводит примеры ошибочных классификаций."""
    misclassified = np.where(y_true != y_pred)[0]
    if len(misclassified) == 0:
        print("\nОшибок нет! Модель идеальна.")
        return

    print(f"\nВсего ошибок: {len(misclassified)} ({len(misclassified)/len(y_true)*100:.1f}%)")

    fp_idx = misclassified[y_pred[misclassified] == 1]
    fn_idx = misclassified[y_pred[misclassified] == 0]

    print(f"  Ложные срабатывания (FP): {len(fp_idx)}")
    print(f"  Пропуски (FN): {len(fn_idx)}")

    if len(fp_idx) > 0:
        print("\nПримеры ложных срабатываний (безопасное → фишинг):")
        for i, idx in enumerate(fp_idx[:num_examples]):
            print(f"  {i+1}. {texts.iloc[idx][:100]}...")

    if len(fn_idx) > 0:
        print("\nПримеры пропусков (фишинг → безопасное):")
        for i, idx in enumerate(fn_idx[:num_examples]):
            print(f"  {i+1}. {texts.iloc[idx][:100]}...")

print("\n" + "=" * 60)
print("АНАЛИЗ ОШИБОК")
print("=" * 60)
analyze_errors(test_df["message"], y_true, y_pred)

print("\n" + "=" * 60)
print("РАБОТА ЗАВЕРШЕНА")
print("=" * 60)