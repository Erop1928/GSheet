from typing import List, Dict, Any
import os
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class LogParser:
    def __init__(self, log_path: str):
        """
        Инициализация парсера логов
        :param log_path: путь к файлу лога
        """
        self.log_path = log_path
        self.logs = []
        self.columns = [
            'Type',
            'Start DateTime',
            'End DateTime',
            'Status Code 1',
            'Error 1',
            'Duration 1',
            'Request ID 1',
            'DateTime 1',
            'Status Code 2',
            'Error 2',
            'Duration 2',
            'Request ID 2',
            'DateTime 2',
            'Status Code 3',
            'Error 3',
            'Duration 3',
            'Request ID 3',
            'DateTime 3',
            'Status Code 4',
            'Error 4',
            'Duration 4',
            'Request ID 4',
            'DateTime 4',
            'Status Code 5',
            'Error 5',
            'Duration 5',
            'Hash',
            'Session ID'
        ]
        self.load_data()
    
    def parse_datetime(self, date_str: str) -> datetime:
        """Парсит строку даты в datetime"""
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d %H:%M:%S.%f %z')
        except ValueError:
            return None
    
    def parse_duration(self, duration_str: str) -> int:
        """Парсит строку длительности в миллисекунды"""
        try:
            return int(duration_str.replace(' ms', ''))
        except (ValueError, AttributeError):
            return 0
    
    def _process_request_data(self, values, start_idx):
        """
        Обрабатывает данные запроса из списка значений
        :param values: список значений
        :param start_idx: начальный индекс для обработки
        :return: словарь с данными запроса и следующий индекс
        """
        request_data = {}
        
        # Status Code
        request_data['Status Code'] = values[start_idx] if start_idx < len(values) else ' '
        
        # Error Message
        error_idx = start_idx + 1
        request_data['Error'] = values[error_idx] if error_idx < len(values) else ' '
        
        # Duration
        duration_idx = start_idx + 2
        duration = values[duration_idx] if duration_idx < len(values) else ' '
        request_data['Duration'] = duration if duration and 'ms' in duration else ' '
        
        # Request ID
        request_id_idx = start_idx + 3
        request_data['Request ID'] = values[request_id_idx] if request_id_idx < len(values) else ' '
        
        # DateTime
        datetime_idx = start_idx + 4
        request_data['DateTime'] = values[datetime_idx] if datetime_idx < len(values) else ' '
        
        return request_data, start_idx + 5

    def load_data(self):
        """Загружает данные из лог файла"""
        with open(self.log_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Пропускаем строки, которые не начинаются с "Summary data"
                if not line.strip().startswith("Summary data"):
                    continue
                    
                # Разбиваем строку по разделителю, сохраняя пустые значения между разделителями
                values = line.strip().split(';')
                if not values:  # Пропускаем пустые строки
                    continue
                
                # Создаем словарь для строки лога с правильным порядком полей
                log_entry = {
                    'Type': values[0],                                    # Summary data
                    'CameraSystemName': values[1] if len(values) > 1 else ' ',  # Первая пустая ячейка
                    'BestShotId': values[2] if len(values) > 2 else ' ',       # Вторая пустая ячейка
                    'Start DateTime': values[3] if len(values) > 3 else ' ',    # Time bestshot received
                    'Quality': values[4] if len(values) > 4 else ' ',          # Quality
                    'QualityErrors': values[5] if len(values) > 5 else ' ',    # QualityErrors
                    'End DateTime': values[6] if len(values) > 6 else ' ',     # Common Time ident request
                }
                
                # Индексы для важных полей
                current_idx = 7  # Начало первого запроса
                
                # Добавляем данные о запросах
                for i in range(1, 6):  # Обрабатываем до 5 запросов
                    if current_idx < len(values):
                        request_data, current_idx = self._process_request_data(values, current_idx)
                        for key, value in request_data.items():
                            log_entry[f'{key} {i}'] = value
                    else:
                        # Если не хватает значений, добавляем пробелы
                        log_entry[f'Status Code {i}'] = ' '
                        log_entry[f'Error {i}'] = ' '
                        log_entry[f'Duration {i}'] = ' '
                        log_entry[f'Request ID {i}'] = ' '
                        log_entry[f'DateTime {i}'] = ' '
                
                # Добавляем Hash и Session ID в конце
                if len(values) > current_idx + 1:
                    log_entry['Hash'] = values[-2] or ' '
                    log_entry['Session ID'] = values[-1] or ' '
                else:
                    log_entry['Hash'] = ' '
                    log_entry['Session ID'] = ' '
                
                # Отладочная информация для проверки разделителей
                print("\nОтладка разделителей:")
                print(f"Исходная строка: {line.strip()}")
                print(f"Количество значений после split: {len(values)}")
                print("Первые 10 значений:")
                for i, v in enumerate(values[:10]):
                    print(f"{i}: '{v}'")
                
                # Добавляем запись в список
                self.logs.append(log_entry)
        
        # Отладочная информация
        if self.logs:
            print("\nОтладка загруженных данных:")
            print(f"Всего записей Summary data: {len(self.logs)}")
            print("Пример первой записи (первые 7 полей):")
            first_entry = self.logs[0]
            fields = ['Type', 'CameraSystemName', 'BestShotId', 'Start DateTime', 'Quality', 'QualityErrors', 'End DateTime']
            for key in fields:
                value = first_entry.get(key, ' ')
                print(f"{key}: '{value}'")
            
            # Показываем значения длительности
            print("\nЗначения длительности в первой записи:")
            for i in range(1, 6):
                duration_key = f'Duration {i}'
                if duration_key in first_entry:
                    print(f"{duration_key}: {first_entry[duration_key]}")
        
        print(f"\nЗагружено {len(self.logs)} записей из лога")
    
    def filter_by_date(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Фильтрует логи по дате
        :param start_date: начальная дата в формате 'YYYY-MM-DD'
        :param end_date: конечная дата в формате 'YYYY-MM-DD'
        :return: отфильтрованный список логов
        """
        filtered_logs = self.logs.copy()
        
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            filtered_logs = [
                log for log in filtered_logs 
                if self.parse_datetime(log.get('Start DateTime', '')) >= start_datetime
            ]
            
        if end_date:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            filtered_logs = [
                log for log in filtered_logs 
                if self.parse_datetime(log.get('Start DateTime', '')) <= end_datetime
            ]
            
        return filtered_logs
    
    def filter_by_status(self, status_codes: List[int]) -> List[Dict]:
        """
        Фильтрует логи по кодам статуса
        :param status_codes: список кодов статуса
        :return: отфильтрованный список логов
        """
        status_codes = [str(code) for code in status_codes]  # Конвертируем в строки
        filtered_logs = []
        
        for log in self.logs:
            # Проверяем все столбцы с кодами статуса
            for i in range(1, 6):
                status_key = f'Status Code {i}'
                if status_key in log and log[status_key] in status_codes:
                    filtered_logs.append(log)
                    break
                    
        return filtered_logs
    
    def filter_by_duration(self, min_duration: int = None, max_duration: int = None) -> List[Dict]:
        """
        Фильтрует логи по длительности выполнения
        :param min_duration: минимальная длительность в мс
        :param max_duration: максимальная длительность в мс
        :return: отфильтрованный список логов
        """
        filtered_logs = []
        
        for log in self.logs:
            # Проверяем все столбцы с длительностью
            for i in range(1, 6):
                duration_key = f'Duration {i}'
                if duration_key in log:
                    duration = self.parse_duration(log[duration_key])
                    
                    if min_duration is not None and duration < min_duration:
                        continue
                    if max_duration is not None and duration > max_duration:
                        continue
                        
                    filtered_logs.append(log)
                    break
                    
        return filtered_logs
    
    def get_statistics(self) -> Dict:
        """
        Получает базовую статистику по логам
        :return: словарь со статистикой
        """
        stats = {
            'total_records': len(self.logs),
            'date_range': {
                'start': None,
                'end': None
            },
            'status_codes': {},
            'avg_duration': {}
        }
        
        if self.logs:
            # Находим диапазон дат
            dates = [self.parse_datetime(log.get('Start DateTime', '')) for log in self.logs]
            dates = [d for d in dates if d is not None]
            if dates:
                stats['date_range']['start'] = min(dates)
                stats['date_range']['end'] = max(dates)
            
            # Собираем статистику по кодам статуса
            for i in range(1, 6):
                status_key = f'Status Code {i}'
                stats['status_codes'][status_key] = {}
                for log in self.logs:
                    if status_key in log:
                        status = log[status_key]
                        stats['status_codes'][status_key][status] = stats['status_codes'][status_key].get(status, 0) + 1
            
            # Собираем статистику по длительности
            for i in range(1, 6):
                duration_key = f'Duration {i}'
                durations = [self.parse_duration(log.get(duration_key, '0 ms')) for log in self.logs]
                if durations:
                    stats['avg_duration'][duration_key] = sum(durations) / len(durations)
        
        return stats
    
    def prepare_for_sheets(self, filtered_logs: List[Dict] = None) -> List[List]:
        """
        Подготавливает данные для записи в Google Sheets
        :param filtered_logs: отфильтрованный список логов
        :return: список списков для записи в таблицу
        """
        MAX_CELL_LENGTH = 40000  # Максимальная длина значения в ячейке
        logs_to_process = filtered_logs if filtered_logs is not None else self.logs
        
        # Подготавливаем заголовки в правильном порядке
        headers = [
            'Type',
            'CameraSystemName',
            'BestShotId',
            'Start DateTime',
            'Quality',
            'QualityErrors',
            'End DateTime',
            'Status Code 1', 'Error 1', 'Duration 1', 'Request ID 1', 'DateTime 1',
            'Status Code 2', 'Error 2', 'Duration 2', 'Request ID 2', 'DateTime 2',
            'Status Code 3', 'Error 3', 'Duration 3', 'Request ID 3', 'DateTime 3',
            'Status Code 4', 'Error 4', 'Duration 4', 'Request ID 4', 'DateTime 4',
            'Status Code 5', 'Error 5', 'Duration 5', 'Request ID 5', 'DateTime 5',
            'Hash',
            'Session ID'
        ]
        
        # Подготавливаем данные
        rows = [headers]
        for log in logs_to_process:
            # Создаем список значений, соответствующий порядку заголовков
            row = []
            for column in headers:
                value = log.get(column, ' ')  # Если значение отсутствует, используем пробел
                
                # Убираем 'ms' из значений длительности
                if 'Duration' in column and value and value.strip():  # Проверяем, что значение не пустое и не состоит только из пробелов
                    print(f"Обработка {column}: исходное значение = '{value}'")  # Отладка
                    try:
                        # Пробуем извлечь числовое значение
                        numeric_value = int(value.replace(' ms', ''))
                        value = str(numeric_value)
                        print(f"  преобразовано в: '{value}'")  # Отладка
                    except (ValueError, AttributeError) as e:
                        print(f"  ошибка преобразования: {e}")  # Отладка
                        value = ' '  # Если не удалось преобразовать, используем пробел
                
                # Преобразуем в строку и проверяем длину
                value = str(value)
                if not value.strip():  # Если строка пустая или состоит только из пробелов
                    value = ' '  # Заменяем на один пробел
                elif len(value) > MAX_CELL_LENGTH:
                    value = value[:MAX_CELL_LENGTH] + '...(truncated)'
                
                row.append(value)
            
            # Проверяем, что длина строки соответствует количеству заголовков
            if len(row) != len(headers):
                print(f"Внимание: длина строки ({len(row)}) не соответствует количеству заголовков ({len(headers)})")
                # Добавляем пробелы, если не хватает столбцов
                while len(row) < len(headers):
                    row.append(' ')
            
            rows.append(row)
            
            # Показываем первую строку для отладки
            if len(rows) == 2:
                print("\nПервая строка данных:")
                for i, (header, value) in enumerate(zip(headers, row)):
                    print(f"{header}: '{value}'")
        
        # Отладочная информация
        print("\nОтладка prepare_for_sheets:")
        print(f"Количество строк: {len(rows)}")
        print(f"Количество столбцов: {len(headers)}")
            
        return rows

def main():
    """Пример использования парсера логов"""
    # Путь к файлу лога
    log_path = 'Logs/cbs-managment-service_log_2024120218.txt'
    print(f"Читаем файл: {log_path}")
    
    # Создаем экземпляр парсера
    parser = LogParser(log_path)
    
    # Выводим информацию о загруженных данных
    print("\nСтруктура данных:")
    print(f"Количество записей: {len(parser.logs)}")
    
    if parser.logs:
        print("\nПример первой записи:")
        for key, value in parser.logs[0].items():
            print(f"{key}: {value}")
    
    # Получаем статистику
    stats = parser.get_statistics()
    print("\nСтатистика по логам:")
    print(f"Всего записей: {stats['total_records']}")
    if stats['date_range']['start']:
        print(f"Диапазон дат: с {stats['date_range']['start']} по {stats['date_range']['end']}")
    
    # Пример фильтрации по статусу
    filtered_logs = parser.filter_by_status([200])
    print(f"\nЗаписи со статусом 200: {len(filtered_logs)}")
    
    # Пример фильтрации по длительности
    filtered_logs = parser.filter_by_duration(min_duration=1000)
    print(f"\nЗаписи с длительностью более 1000 мс: {len(filtered_logs)}")
    
    # Получаем данные для Google Sheets
    sheets_data = parser.prepare_for_sheets(filtered_logs)
    print(f"\nПодготовлено строк для записи в таблицу: {len(sheets_data)}")

if __name__ == '__main__':
    main() 