@echo off

chcp 65001 >nul
setlocal enabledelayedexpansion


set "venv_path=venv"
set "project_path=%cd%"


if not exist "%project_path%\%venv_path%\" (
    echo Создание виртуального окружения...
    python -m venv "%project_path%\%venv_path%"
    if errorlevel 1 (
        echo Ошибка: Не удалось создать виртуальное окружение
        exit /b 1
    )
)


call "%project_path%\%venv_path%\Scripts\activate"
if errorlevel 1 (
    echo Ошибка: Не удалось активировать виртуальное окружение
    exit /b 1
)


if exist requirements.txt (
    echo Установка зависимостей...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Ошибка: Не удалось установить зависимости
        exit /b 1
    )
) else (
    echo Ошибка: Файл requirements.txt не найден
    exit /b 1
)

echo Виртуальное окружение успешно создано и активировано. Зависимости установлены.
exit /b 0
