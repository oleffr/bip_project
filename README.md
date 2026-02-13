# bip_project-0.0

## Чтобы создать виртультальное окружение и запустить:

``` powershell
python -m venv venv   
.\venv\Scripts\Activate.ps1   
pip install django   
django-admin startproject myproject   
cd myproject   
python manage.py startapp main   
# Создание базы данных 
python manage.py migrate 
# Создание суперпользователя (для админки) 
python manage.py createsuperuser
# Запуск сервера 
python manage.py runserver
```

Основные файлы, которые написаны минимально:
 - myproject/urls.py
 - myproject/setting.py
 - main/views.py
 - templates/*