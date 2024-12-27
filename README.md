# Google Sheets Log Uploader

Скрипт для автоматической загрузки данных из лог-файлов в Google Sheets.

## Требования

- CentOS 7 или выше
- Python 3.6 или выше
- Доступ к Google Sheets API
- Сервисный аккаунт Google с доступом к таблице

## Структура проекта

```
.
├── parser.py           # Парсер лог-файлов
├── sheets_uploader.py  # Загрузчик данных в Google Sheets
├── requirements.txt    # Зависимости Python
├── install.sh         # Скрипт установки
├── run_uploader.sh    # Скрипт запуска
├── .env              # Конфигурация (создается при установке)
└── README.md         # Документация
```

## Установка

1. Подготовка:
   ```bash
   # Клонируем репозиторий
   git clone <repository_url>
   cd gsheet_uploader
   ```

2. Настройка Google Sheets:
   - Создайте проект в Google Cloud Console
   - Включите Google Sheets API
   - Создайте сервисный аккаунт и скачайте JSON-ключ
   - Переименуйте JSON-ключ в `fair-root-445807-i5-aa2407460343.json`
   - Предоставьте доступ к таблице для сервисного аккаунта

3. Создайте файл `.env`:
   ```
   SPREADSHEET_ID=ваш_id_таблицы
   ```

4. Запустите установку:
   ```bash
   chmod +x install.sh
   sudo ./install.sh
   ```

## Использование

Скрипт автоматически запускается каждый час через cron и обрабатывает все .txt файлы в указанной директории.

### Ручной запуск

```bash
/opt/gsheet_uploader/run_uploader.sh
```

### Проверка логов

```bash
tail -f /var/log/gsheet_uploader/uploader_YYYYMMDD.log  # Логи скрипта
tail -f /var/log/gsheet_uploader/cron.log               # Логи cron
```

## Структура лог-файлов

Скрипт ожидает лог-файлы в формате:
```
Summary data;;;YYYY-MM-DD HH:MM:SS.mmm +00:00;;;...
```

## Обслуживание

### Логротация

Логи автоматически ротируются ежедне��но и хранятся 7 дней.

### Мониторинг

Проверьте статус выполнения:
```bash
grep "ERROR" /var/log/gsheet_uploader/uploader_*.log
```

## Безопасность

- Все конфиденциальные файлы имеют права доступа 600
- Скрипт запускается от отдельного пользователя gsheet_user
- Учетные данные Google хранятся в защищенном файле

## Устранение неполадок

1. Проверьте права доступа:
   ```bash
   ls -l /opt/gsheet_uploader/
   ls -l /var/log/gsheet_uploader/
   ```

2. Проверьте cron:
   ```bash
   sudo crontab -u gsheet_user -l
   ```

3. Проверьте логи:
   ```bash
   tail -f /var/log/gsheet_uploader/*.log
   ``` 