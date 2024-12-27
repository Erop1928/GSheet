#!/bin/bash

# Проверяем, что скрипт запущен от root
if [ "$EUID" -ne 0 ]; then 
    echo "Пожалуйста, запустите скрипт от имени root"
    exit 1
fi

# Устанавливаем Python 3 и pip, если их нет
if ! command -v python3 &> /dev/null; then
    echo "Установка Python 3..."
    yum install -y python3
fi

if ! command -v pip3 &> /dev/null; then
    echo "Установка pip3..."
    yum install -y python3-pip
fi

# Создаем пользователя для запуска скрипта, если его нет
if ! id -u gsheet_user &>/dev/null; then
    echo "Создание пользователя gsheet_user..."
    useradd -m -s /bin/bash gsheet_user
fi

# Устанавливаем проект
PROJECT_PATH="/opt/gsheet_uploader"
VENV_PATH="$PROJECT_PATH/venv"
LOGS_PATH="/var/log/gsheet_uploader"

# Создаем необходимые директории
echo "Создание директорий проекта..."
mkdir -p $PROJECT_PATH
mkdir -p $LOGS_PATH

# Копируем файлы проекта
echo "Копирование файлов проекта..."
cp -r ./* $PROJECT_PATH/

# Создаем виртуальное окружение
echo "Создание виртуального окружения..."
python3 -m venv $VENV_PATH

# Активируем виртуальное окружение и устанавливаем зависимости
echo "Установка зависимостей..."
source $VENV_PATH/bin/activate
pip install -r $PROJECT_PATH/requirements.txt
deactivate

# Обновляем пути в run_uploader.sh
echo "Настройка run_uploader.sh..."
sed -i "s|/path/to/your/venv|$VENV_PATH|g" $PROJECT_PATH/run_uploader.sh
sed -i "s|/path/to/project|$PROJECT_PATH|g" $PROJECT_PATH/run_uploader.sh
sed -i "s|/path/to/logs|$LOGS_PATH|g" $PROJECT_PATH/run_uploader.sh

# Делаем скрипты исполняемыми
chmod +x $PROJECT_PATH/run_uploader.sh

# Устанавливаем права доступа
echo "Настройка прав доступа..."
chown -R gsheet_user:gsheet_user $PROJECT_PATH
chown -R gsheet_user:gsheet_user $LOGS_PATH
chmod 755 $PROJECT_PATH
chmod 755 $LOGS_PATH
chmod 600 $PROJECT_PATH/.env
chmod 600 $PROJECT_PATH/fair-root-445807-i5-aa2407460343.json

# Добавляем задачу в crontab для пользователя gsheet_user
echo "Настройка crontab..."
(crontab -u gsheet_user -l 2>/dev/null || echo "") | { cat; echo "0 * * * * $PROJECT_PATH/run_uploader.sh >> $LOGS_PATH/cron.log 2>&1"; } | crontab -u gsheet_user -

# Создаем systemd сервис для логротации
echo "Настройка логротации..."
cat > /etc/logrotate.d/gsheet_uploader << EOF
$LOGS_PATH/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 gsheet_user gsheet_user
}
EOF

echo "Установка завершена!"
echo "Проект установлен в: $PROJECT_PATH"
echo "Логи будут сохраняться в: $LOGS_PATH"
echo "Скрипт будет запускаться каждый час от имени пользователя gsheet_user" 