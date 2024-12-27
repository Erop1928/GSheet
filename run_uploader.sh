#!/bin/bash

# Путь к виртуальному окружению Python
VENV_PATH="/path/to/your/venv"

# Путь к директории с проектом
PROJECT_PATH="/path/to/project"

# Путь к директории с логами для обработки
LOGS_PATH="/path/to/logs"

# Активируем виртуальное окружение
source $VENV_PATH/bin/activate

# Переходим в директорию проекта
cd $PROJECT_PATH

# Запускаем скрипт
python sheets_uploader.py $LOGS_PATH

# Деактивируем виртуальное окружение
deactivate 