from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd
import os

# Загружаем переменные окружения
load_dotenv()

# Путь к файлу с учетными данными сервисного аккаунта
CREDENTIALS_FILE = 'fair-root-445807-i5-aa2407460343.json'  # Убедитесь, что файл находится в той же директории

# Область доступа
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_service():
    """Создает объект service для работы с Google Sheets API"""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    return service

def read_range(spreadsheet_id, range_name):
    """Читает данные из указанного диапазона"""
    service = get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    return result.get('values', [])

def write_range(spreadsheet_id, range_name, values):
    """Записывает данные в указанный диапазон"""
    service = get_service()
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()
    return result

def create_spreadsheet(title):
    """Создает новую таблицу с указанным названием"""
    service = get_service()
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet).execute()
    return spreadsheet.get('spreadsheetId')

def share_spreadsheet(spreadsheet_id, email, role='writer'):
    """Предоставляет доступ к таблице по email
    role может быть: 'writer', 'reader', 'owner'
    """
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, 
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    
    drive_service = build('drive', 'v3', credentials=credentials)
    
    def callback(request_id, response, exception):
        if exception:
            print(f'Ошибка предоставления доступа: {exception}')
        else:
            print(f'Доступ предоставлен успешно')
    
    batch = drive_service.new_batch_http_request(callback=callback)
    user_permission = {
        'type': 'user',
        'role': role,
        'emailAddress': email
    }
    batch.add(drive_service.permissions().create(
        fileId=spreadsheet_id,
        body=user_permission,
        fields='id',
        sendNotificationEmail=False
    ))
    batch.execute()

def upload_excel_to_sheets(excel_path, sheet_title=None):
    """Создает новую Google таблицу из Excel файла"""
    # Читаем Excel файл
    df = pd.read_excel(excel_path)
    
    # Очищаем DataFrame от пустых столбцов
    df = df.dropna(axis=1, how='all')
    
    # Заменяем NaN на пустые строки
    df = df.fillna('')
    
    # Очищаем названия столбцов от 'Unnamed: X'
    df.columns = [col if not col.startswith('Unnamed:') else f'Столбец {i+1}'
                 for i, col in enumerate(df.columns)]
    
    # Если название не указано, используем имя файла
    if sheet_title is None:
        sheet_title = os.path.splitext(os.path.basename(excel_path))[0]
    
    # Создаем новую таблицу
    spreadsheet_id = create_spreadsheet(sheet_title)
    
    # Преобразуем DataFrame в список списков
    values = [df.columns.tolist()] + df.values.tolist()
    
    # Записываем данные
    range_name = f'Sheet1!A1:{chr(64 + len(df.columns))}{len(values)}'
    write_range(spreadsheet_id, range_name, values)
    
    return spreadsheet_id

if __name__ == '__main__':
    # Загружаем Excel файл в Google Sheets
    EXCEL_PATH = 'sheet.xlsx'
    SPREADSHEET_ID = upload_excel_to_sheets(EXCEL_PATH, 'Импортированная таблица')
    print(f'Создана новая таблица с ID: {SPREADSHEET_ID}')
    
    # Предоставляем доступ
    USER_EMAIL = 'erop1928@gmail.com'
    share_spreadsheet(SPREADSHEET_ID, USER_EMAIL, role='writer')
    print(f'URL таблицы: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}') 