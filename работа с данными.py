import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

# Настройка визуализаций
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")

# Загрузка датасета
def load_sms_data():
    """
    Загружает датасет SMS Spam Collection.
    """
    # URL файла данных (сырой файл с UCI)
   
    # В данном случае проще скачать и использовать локальный файл 'SMSSpamCollection'
    # Предполагается, что файл находится в текущей директории
    try:
        # Чтение данных, разделенных табуляцией, без заголовка
        df = pd.read_csv('SMSSpamCollection', sep='\t', header=None, names=['label', 'message'])
        print(" Данные успешно загружены!")
        return df
    except FileNotFoundError:
        print(" Файл 'SMSSpamCollection' не найден. Убедитесь, что он находится в правильной директории.")
        return None

# Загружаем данные
df = load_sms_data()

# Выводим основную информацию о датасете
def analyze_sms_dataset(df):
    """
    Проводит базовый анализ датасета SMS.
    """
    print("\n" + "="*50)
    print("ПЕРВИЧНЫЙ АНАЛИЗ ДАННЫХ")
    print("="*50)
    
    print(f"Размер датасета: {df.shape[0]} сообщений, {df.shape[1]} столбцов")
    print("\nПервые 5 записей:")
    print(df.head())
    
    print("\nИнформация о датасете:")
    print(df.info())
    
    print("\nРаспределение меток:")
    print(df['label'].value_counts())
    print(df['label'].value_counts(normalize=True))
    
    # Проверка на пропущенные значения
    print(f"\nПропущенные значения: {df.isnull().sum().sum()}")
    
    # Добавим длину каждого сообщения для анализа
    df['message_length'] = df['message'].apply(len)
    print(f"\nСредняя длина сообщения: {df['message_length'].mean():.2f} символов")
    
    return df

# Проводим анализ
if df is not None:
    df = analyze_sms_dataset(df)

# ===========================================================================================

# Разделение данных на обучающую, валидационную и тестовую выборки
def split_sms_data(df, test_size=0.15, val_size=0.15, random_state=42):
    """
    Разделяет датасет SMS на обучающую, валидационную и тестовую выборки
    с сохранением пропорций классов (стратификация)
    """
    print("\n" + "="*50)
    print("РАЗДЕЛЕНИЕ ДАННЫХ НА ВЫБОРКИ")
    print("="*50)
    
    # Создаем числовую кодировку меток для стратификации
    df['label_encoded'] = df['label'].map({'ham': 0, 'spam': 1})
    
    # Сначала разделяем на временную (temp) и тестовую выборки
    temp_df, test_df = train_test_split(
        df, 
        test_size=test_size, 
        random_state=random_state, 
        stratify=df['label_encoded']  # Сохраняем пропорции классов
    )
    
    # Затем временную выборку разделяем на обучающую и валидационную
    val_ratio = val_size / (1 - test_size)  # Пересчитываем ratio
    train_df, val_df = train_test_split(
        temp_df, 
        test_size=val_ratio, 
        random_state=random_state, 
        stratify=temp_df['label_encoded']
    )
    
    # Извлекаем фичи и таргеты для каждой выборки
    X_train = train_df['message']
    y_train = train_df['label_encoded']
    
    X_val = val_df['message']
    y_val = val_df['label_encoded']
    
    X_test = test_df['message']
    y_test = test_df['label_encoded']
    
    # Выводим информацию о размерах выборок
    total_samples = len(df)
    print("РАЗМЕРЫ ВЫБОРОК:")
    print(f"    Обучающая выборка: {len(X_train)} samples ({len(X_train)/total_samples*100:.1f}%)")
    print(f"    Валидационная выборка: {len(X_val)} samples ({len(X_val)/total_samples*100:.1f}%)")
    print(f"    Тестовая выборка: {len(X_test)} samples ({len(X_test)/total_samples*100:.1f}%)")
    
    # Проверяем распределение классов в каждой выборке
    print("\nРАСПРЕДЕЛЕНИЕ КЛАССОВ ПО ВЫБОРКАМ:")
    for name, X_data, y_data in [("Обучающая", X_train, y_train), 
                                ("Валидационная", X_val, y_val), 
                                ("Тестовая", X_test, y_test)]:
        spam_count = y_data.sum()
        ham_count = len(y_data) - spam_count
        spam_ratio = spam_count / len(y_data) * 100
        ham_ratio = ham_count / len(y_data) * 100
        print(f"   • {name:15}: {spam_count:3d} спам ({spam_ratio:.1f}%), {ham_count:4d} не спам ({ham_ratio:.1f}%)")
    
    return X_train, X_val, X_test, y_train, y_val, y_test

# Разделяем данные
X_train, X_val, X_test, y_train, y_val, y_test = split_sms_data(df)

def save_split_data(X_train, X_val, X_test, y_train, y_val, y_test, df):
    """
    Сохраняет разделенные данные для последующего использования
    """
    import joblib
    import os
    
    # Создаем папку для сохранения
    os.makedirs('sms_split_data', exist_ok=True)
    
    # Сохраняем данные в формате pandas
    train_data = pd.DataFrame({'message': X_train, 'label': y_train})
    val_data = pd.DataFrame({'message': X_val, 'label': y_val})
    test_data = pd.DataFrame({'message': X_test, 'label': y_test})
    
    # Сохраняем как CSV
    train_data.to_csv('sms_split_data/train.csv', index=False)
    val_data.to_csv('sms_split_data/validation.csv', index=False)
    test_data.to_csv('sms_split_data/test.csv', index=False)
    
    # Сохраняем как pickle для быстрой загрузки
    joblib.dump(X_train, 'sms_split_data/X_train.pkl')
    joblib.dump(X_val, 'sms_split_data/X_val.pkl')
    joblib.dump(X_test, 'sms_split_data/X_test.pkl')
    joblib.dump(y_train, 'sms_split_data/y_train.pkl')
    joblib.dump(y_val, 'sms_split_data/y_val.pkl')
    joblib.dump(y_test, 'sms_split_data/y_test.pkl')
    
    # Сохраняем полный датасет с индексами выборок
    df_with_split = df.copy()
    df_with_split['split'] = 'unknown'
    df_with_split.loc[df['message'].isin(X_train), 'split'] = 'train'
    df_with_split.loc[df['message'].isin(X_val), 'split'] = 'validation'
    df_with_split.loc[df['message'].isin(X_test), 'split'] = 'test'
    
    df_with_split.to_csv('sms_split_data/full_dataset_with_split.csv', index=False)
    df_with_split.to_pickle('sms_split_data/full_dataset_with_split.pkl')
    
    print("\n Данные успешно сохранены в папку 'sms_split_data/'")
    print(" Файлы:")
    print("    train.csv, validation.csv, test.csv")
    print("    X_train.pkl, X_val.pkl, X_test.pkl")
    print("    y_train.pkl, y_val.pkl, y_test.pkl")
    print("    full_dataset_with_split.csv/.pkl")

# Сохраняем разделенные данные
save_split_data(X_train, X_val, X_test, y_train, y_val, y_test, df)