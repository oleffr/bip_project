@echo off

chcp 65001 >nul
setlocal enabledelayedexpansion


set "venv_path=venv"
set "project_path=%cd%"


if not exist "%project_path%\%venv_path%\" (
    echo Ошибка: Нет виртуального окружения
    exit /b 1
    
)


call "%project_path%\%venv_path%\Scripts\activate"
if errorlevel 1 (
    echo Ошибка: Не удалось активировать виртуальное окружение
    exit /b 1
)


pip freeze > requirements.txt
if errorlevel 1 (
    echo Ошибка: Не удалось обновить Зависимости
    exit /b 1
)


echo Файл зависимостей обновлен
exit /b 0
