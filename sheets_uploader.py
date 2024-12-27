import pygsheets
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from parser import LogParser

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, f'uploader_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

def col_num_to_letter(n):
    """Преобразует номер столбца в букву (A=1, B=2, ..., Z=26, AA=27, ...)"""
    result = ''
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

class SheetsUploader:
    def __init__(self):
        self.credentials_file = 'fair-root-445807-i5-aa2407460343.json'
        self.spreadsheet_id = os.getenv('SPREADSHEET_ID')
        self.client = self._get_client()
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        self.worksheet = self.spreadsheet.sheet1
        self._ensure_headers()
        self.existing_data = self._get_existing_data()
    
    def _get_client(self):
        """Создает клиент pygsheets"""
        return pygsheets.authorize(service_file=self.credentials_file)
    
    def _get_existing_data(self):
        """Получает существующие данные из таблице по столбцам D и G"""
        try:
            start_dates = self.worksheet.get_col(4, include_empty=False)
            end_dates = self.worksheet.get_col(7, include_empty=False)
            existing_records = set()
            
            for start_date, end_date in zip(start_dates[1:], end_dates[1:]):
                if start_date and end_date:
                    record_id = f"{start_date}_{end_date}"
                    existing_records.add(record_id)
            
            logging.info(f"Загружено {len(existing_records)} существующих записей")
            return existing_records
            
        except Exception as e:
            logging.error(f"Ошибка при получении существующих данных: {e}")
            return set()
    
    def _filter_duplicates(self, data):
        """Фильтрует дубликаты из новых данных по столбцам D и G"""
        if len(data) <= 1:
            return data
        
        try:
            start_dt_idx = 3  # D = 4-й столбец (индекс 3)
            end_dt_idx = 6    # G = 7-й столбец (индекс 6)
            
            filtered_data = [data[0]]  # Сохраняем заголовки
            duplicates_count = 0
            
            for row in data[1:]:
                if len(row) > max(start_dt_idx, end_dt_idx):
                    record_id = f"{row[start_dt_idx]}_{row[end_dt_idx]}"
                    if record_id not in self.existing_data:
                        filtered_data.append(row)
                        self.existing_data.add(record_id)
                    else:
                        duplicates_count += 1
            
            logging.info(f"Найдено {duplicates_count} дубликатов")
            logging.info(f"Осталось {len(filtered_data) - 1} уникальных записей")
            return filtered_data
            
        except Exception as e:
            logging.error(f"Ошибка при фильтрации дубликатов: {e}")
            return data
    
    def _ensure_sheet_size(self, required_rows):
        """Проверяет и при необходимости расширяет размер таблицы"""
        try:
            current_rows = self.worksheet.rows
            if required_rows > current_rows:
                new_rows = required_rows + 1000
                self.worksheet.resize(rows=new_rows)
                logging.info(f"Таблица расширена до {new_rows} строк")
                
        except Exception as e:
            logging.error(f"Ошибка при расширении таблицы: {e}")
    
    def _ensure_headers(self):
        """Проверяет и при необходимости создает заголовки в таблице"""
        try:
            headers = self.worksheet.get_row(1)
            required_headers = [
                'Type', 'CameraSystemName', 'BestShotId', 'Start DateTime',
                'Quality', 'QualityErrors', 'End DateTime',
                'Status Code 1', 'Error 1', 'Duration 1', 'Request ID 1', 'DateTime 1',
                'Status Code 2', 'Error 2', 'Duration 2', 'Request ID 2', 'DateTime 2',
                'Status Code 3', 'Error 3', 'Duration 3', 'Request ID 3', 'DateTime 3',
                'Status Code 4', 'Error 4', 'Duration 4', 'Request ID 4', 'DateTime 4',
                'Status Code 5', 'Error 5', 'Duration 5', 'Request ID 5', 'DateTime 5',
                'Hash', 'Session ID'
            ]
            
            if not headers or headers != required_headers:
                logging.info("Обновление заголовков таблицы...")
                self.worksheet.update_row(1, required_headers)
                logging.info("Заголовки обновлены")
            
        except Exception as e:
            logging.error(f"Ошибка при проверке/создании заголовков: {e}")
    
    def upload_data(self, data):
        """Добавляет новые данные в конец таблицы"""
        try:
            if not data or len(data) <= 1:
                logging.info("Нет данных для загрузки")
                return True
            
            filtered_data = self._filter_duplicates(data)
            
            if len(filtered_data) <= 1:
                logging.info("После фильтрации дубликатов нет данных для загрузки")
                return True
            
            last_row = len(self.worksheet.get_col(1, include_empty=False))
            next_row = last_row + 1
            
            required_rows = next_row + len(filtered_data) - 1
            self._ensure_sheet_size(required_rows)
            
            values = filtered_data[1:]
            last_col = len(filtered_data[0])
            last_col_letter = col_num_to_letter(last_col)
            
            start_cell = f'A{next_row}'
            end_cell = f'{last_col_letter}{next_row + len(values) - 1}'
            
            self.worksheet.update_values(
                crange=f'{start_cell}:{end_cell}',
                values=values
            )
            
            logging.info(f"Добавлено {len(values)} новых строк")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка при добавлении данных: {e}")
            return False

def main():
    try:
        # Проверяем наличие аргумента с путем к директории
        if len(sys.argv) < 2:
            logging.error("Не указан путь к директории с логами")
            logging.error("Использование: python sheets_uploader.py путь/к/директории")
            sys.exit(1)
        
        logs_dir = sys.argv[1]
        
        if not os.path.exists(logs_dir):
            logging.error(f"Директория {logs_dir} не найдена")
            sys.exit(1)
        
        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.txt')]
        
        if not log_files:
            logging.info(f"В директории {logs_dir} не найдено лог-файлов")
            sys.exit(0)
        
        logging.info(f"Найдено {len(log_files)} лог-файлов")
        uploader = SheetsUploader()
        
        for log_file in sorted(log_files):
            log_path = os.path.join(logs_dir, log_file)
            logging.info(f"Обработка файла: {log_file}")
            
            try:
                parser = LogParser(log_path)
                data = parser.prepare_for_sheets()
                
                if len(data) > 1:
                    uploader.upload_data(data)
                    
            except Exception as e:
                logging.error(f"Ошибка при обработке файла {log_file}: {e}")
                continue
        
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 