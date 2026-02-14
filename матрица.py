import torch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer
from datasets import Dataset
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, precision_recall_fscore_support, roc_curve, auc
import os

print(" ЗАГРУЗКА ОБУЧЕННОЙ МОДЕЛИ ДЛЯ АНАЛИЗА")
print("=" * 60)

# Параметры
model_path = "final_model"  
test_data_path = "sms_split_data/test.csv" 

# Загрузка тестовых данных
print(" Загрузка тестовых данных...")
test_data = pd.read_csv(test_data_path)
X_test = test_data['message']
y_test = test_data['label_encoded']

print(f" Загружено {len(X_test)} тестовых сообщений")
print(f"    Спам: {y_test.sum()}")
print(f"    Не спам: {len(y_test) - y_test.sum()}")

# Загрузка токенизатора и модели
print("\n Загрузка модели и токенизатора...")
try:
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    print(" Модель и токенизатор успешно загружены!")
except Exception as e:
    print(f" Ошибка загрузки: {e}")
    exit()

# Функция для токенизации
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=128,
        return_tensors="pt"
    )

# Подготовка тестового датасета
print("\n Подготовка данных для модели...")
test_dict = {"text": X_test.tolist(), "label": y_test.tolist()}
test_dataset = Dataset.from_dict(test_dict)
tokenized_test = test_dataset.map(tokenize_function, batched=True, batch_size=16)
tokenized_test = tokenized_test.remove_columns(['text'])

# Создание Trainer для предсказаний
trainer = Trainer(
    model=model,
    tokenizer=tokenizer,
)

# Получение предсказаний
print("\n Получение предсказаний модели...")
predictions = trainer.predict(tokenized_test)
y_pred = np.argmax(predictions.predictions, axis=1)
y_true = predictions.label_ids

# Получение вероятностей для класса 1 (спам) для ROC-AUC
y_scores = torch.softmax(torch.tensor(predictions.predictions), dim=1).numpy()[:, 1]
# Функция для построения матрицы ошибок
def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Не спам', 'Спам'],
                yticklabels=['Не спам', 'Спам'],
                cbar_kws={'label': 'Количество сообщений'})
    
    plt.title('Матрица ошибок спам-фильтра\n', fontsize=16, fontweight='bold')
    plt.ylabel('Реальные метки', fontsize=14)
    plt.xlabel('Предсказанные метки', fontsize=14)
    plt.tight_layout()
    plt.show()
    
    return cm

# Построение матрицы ошибок
print("\n Построение матрицы ошибок...")
cm = plot_confusion_matrix(y_true, y_pred)

# Детальный анализ результатов
print("\n" + "=" * 60)
print(" ДЕТАЛЬНЫЙ АНАЛИЗ РЕЗУЛЬТАТОВ")
print("=" * 60)

# Вычисление метрик
accuracy = accuracy_score(y_true, y_pred)
precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')

tn, fp, fn, tp = cm.ravel()

print(f"\n МАТРИЦА ОШИБОК:")
print(f"                 | Предсказан 'Не спам' | Предсказан 'Спам'")
print(f"-----------------|----------------------|-------------------")
print(f"Реальный 'Не спам' | {tn:>20} | {fp:>15}")
print(f"Реальный 'Спам'    | {fn:>20} | {tp:>15}")

print(f"\n ОСНОВНЫЕ МЕТРИКИ:")
print(f" Точность (Accuracy):  {accuracy:.4f}")
print(f" Точность (Precision): {precision:.4f}")
print(f" Полнота (Recall):     {recall:.4f}")
print(f" F1-мера:             {f1:.4f}")

print(f"\n ИНТЕРПРЕТАЦИЯ:")
print(f" True Negative (TN):  {tn} - правильно распознанные НЕ спам сообщения")
print(f" False Positive (FP): {fp} - НЕ спам, ошибочно помеченные как спам")
print(f" False Negative (FN): {fn} - спам, пропущенный фильтром")
print(f" True Positive (TP):  {tp} - правильно распознанный спам")

# Анализ качества
print(f"\n  АНАЛИЗ КАЧЕСТВА:")
if fp > fn:
    print(" Модель СЛИШКОМ АГРЕССИВНА - много ложных срабатываний")
    print(" Риск: потеря важных сообщений")
elif fn > fp:
    print(" Модель СЛИШКОМ МЯГКАЯ - пропускает много спама")
    print(" Риск: пользователь получит нежелательные сообщения")
else:
    print(" Модель ХОРОШО СБАЛАНСИРОВАНА")

# Детальный отчет классификации
print(f"\n ДЕТАЛЬНЫЙ ОТЧЕТ КЛАССИФИКАЦИИ:")
print(classification_report(y_true, y_pred, target_names=['Не спам', 'Спам']))

# Анализ примеров ошибок
def analyze_errors(X_test, y_true, y_pred, num_examples=3):
    print(f"\n" + "=" * 60)
    print(" АНАЛИЗ ОШИБОК МОДЕЛИ")
    print("=" * 60)
    
    misclassified_indices = np.where(y_true != y_pred)[0]
    
    if len(misclassified_indices) == 0:
        print(" Модель не сделала ни одной ошибки!")
        return
    
    print(f"Всего ошибок: {len(misclassified_indices)} ({len(misclassified_indices)/len(y_true)*100:.1f}%)")
    
    # Ложные срабатывания (FP)
    fp_indices = misclassified_indices[y_pred[misclassified_indices] == 1]
    # Пропуски спама (FN)
    fn_indices = misclassified_indices[y_pred[misclassified_indices] == 0]
    
    print(f"• Ложные срабатывания (FP): {len(fp_indices)}")
    print(f"• Пропуски спама (FN): {len(fn_indices)}")
    
    # Примеры ложных срабатываний
    if len(fp_indices) > 0:
        print(f"\n ЛОЖНЫЕ СРАБАТЫВАНИЯ (FP) - примеры:")
        for i, idx in enumerate(fp_indices[:num_examples]):
            message = X_test.iloc[idx] if hasattr(X_test, 'iloc') else X_test[idx]
            print(f"  {i+1}. '{message}'")
    
    # Примеры пропусков спама
    if len(fn_indices) > 0:
        print(f"\n ПРОПУЩЕННЫЙ СПАМ (FN) - примеры:")
        for i, idx in enumerate(fn_indices[:num_examples]):
            message = X_test.iloc[idx] if hasattr(X_test, 'iloc') else X_test[idx]
            print(f"  {i+1}. '{message}'")

# Запуск анализа ошибок
analyze_errors(X_test, y_true, y_pred)


# Функция для построения ROC-кривой
def plot_roc_curve(y_true, y_scores):
    # Вычисление ROC-кривой и AUC
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    
    # Построение графика
    plt.figure(figsize=(10, 8))
    plt.plot(fpr, tpr, color='darkorange', lw=2, 
             label=f'ROC-кривая (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
             label='Случайный классификатор')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (Доля ложных срабатываний)', fontsize=14)
    plt.ylabel('True Positive Rate (Полнота)', fontsize=14)
    plt.title('ROC-кривая спам-фильтра\n', fontsize=16, fontweight='bold')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    
    # Добавление дополнительной информации
    plt.text(0.6, 0.3, f'AUC = {roc_auc:.4f}', fontsize=14,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
    
    plt.tight_layout()
    plt.show()
    
    return roc_auc, fpr, tpr

print("\n Построение ROC-кривой...")
roc_auc, fpr, tpr = plot_roc_curve(y_true, y_scores)

print("\n" + "=" * 60)
print(" АНАЛИЗ ЗАВЕРШЕН!")
print("=" * 60)