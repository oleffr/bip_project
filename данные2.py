import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

print("🔄 ПЕРЕСОЗДАНИЕ ДАННЫХ...")

# Загрузка исходного датасета
def load_original_data():
    """
    Загружает оригинальный датасет SMS Spam Collection
    """
    try:
        # Чтение данных, разделенных табуляцией, без заголовка
        df = pd.read_csv('SMSSpamCollection', sep='\t', header=None, names=['label', 'message'])
        print(" Оригинальные данные загружены!")
        return df
    except FileNotFoundError:
        print(" Файл 'SMSSpamCollection' не найден.")
        return None

# Загрузка оригинальных данных
df = load_original_data()

if df is None:
    print("не удалось загрузить данные. Убедитесь, что файл 'SMSSpamCollection' находится в текущей директории.")
    exit()

# Разделение данных на обучающую, валидационную и тестовую выборки
def split_and_save_data(df, test_size=0.15, val_size=0.15, random_state=42):
    """
    Разделяет данные и сохраняет в надежном формате
    """
    print("\n РАЗДЕЛЕНИЕ ДАННЫХ...")
    
    # Создаем числовую кодировку меток
    df['label_encoded'] = df['label'].map({'no spam': 0, 'spam': 1})
    
    # Разделяем на временную и тестовую выборки
    temp_df, test_df = train_test_split(
        df, 
        test_size=test_size, 
        random_state=random_state, 
        stratify=df['label_encoded']
    )
    
    # Разделяем временную на обучающую и валидационную
    val_ratio = val_size / (1 - test_size)
    train_df, val_df = train_test_split(
        temp_df, 
        test_size=val_ratio, 
        random_state=random_state, 
        stratify=temp_df['label_encoded']
    )
    
    # Создаем папку для данных
    os.makedirs('sms_split_data', exist_ok=True)
    
    # Сохраняем в CSV (более надежный формат)
    train_df[['message', 'label_encoded']].to_csv('sms_split_data/train.csv', index=False)
    val_df[['message', 'label_encoded']].to_csv('sms_split_data/validation.csv', index=False)
    test_df[['message', 'label_encoded']].to_csv('sms_split_data/test.csv', index=False)
    
    # Также сохраняем в pickle с протоколом для совместимости
    train_df[['message', 'label_encoded']].to_pickle('sms_split_data/train.pkl', protocol=4)
    val_df[['message', 'label_encoded']].to_pickle('sms_split_data/validation.pkl', protocol=4)
    test_df[['message', 'label_encoded']].to_pickle('sms_split_data/test.pkl', protocol=4)
    
    print(" Данные успешно разделены и сохранены!")
    print(f"    Обучающая выборка: {len(train_df)} сообщений")
    print(f"    Валидационная выборка: {len(val_df)} сообщений")
    print(f"    Тестовая выборка: {len(test_df)} сообщений")
    
    return train_df, val_df, test_df

# Пересоздаем данные
train_df, val_df, test_df = split_and_save_data(df)

# Теперь загружаем данные из CSV (более надежно)
def load_data_safely():
    """
    Загружает данные из CSV файлов
    """
    print("\n БЕЗОПАСНАЯ ЗАГРУЗКА ДАННЫХ...")
    
    try:
        # Загрузка из CSV
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
        return X_train, X_val, X_test, y_train, y_val, y_test
        
    except Exception as e:
        print(f" Ошибка загрузки из CSV: {e}")
        
        # Попробуем загрузить из pickle с обработкой ошибок
        try:
            X_train = pd.read_pickle('sms_split_data/train.pkl')['message']
            y_train = pd.read_pickle('sms_split_data/train.pkl')['label_encoded']
            
            X_val = pd.read_pickle('sms_split_data/validation.pkl')['message']
            y_val = pd.read_pickle('sms_split_data/validation.pkl')['label_encoded']
            
            X_test = pd.read_pickle('sms_split_data/test.pkl')['message']
            y_test = pd.read_pickle('sms_split_data/test.pkl')['label_encoded']
            
            print(" Данные загружены из pickle!")
            return X_train, X_val, X_test, y_train, y_val, y_test
            
        except Exception as e2:
            print(f" Ошибка загрузки из pickle: {e2}")
            return None, None, None, None, None, None

# Загружаем данные безопасным способом
X_train, X_val, X_test, y_train, y_val, y_test = load_data_safely()

if X_train is None:
    print(" Критическая ошибка: не удалось загрузить данные.")
    exit()

print(f" Финальная проверка:")
print(f"    X_train: {len(X_train)} сообщений")
print(f"    X_val: {len(X_val)} сообщений")
print(f"    X_test: {len(X_test)} сообщений")