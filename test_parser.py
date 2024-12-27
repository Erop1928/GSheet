from parser import LogParser

def test_single_line():
    # Создаем парсер
    parser = LogParser('Logs/cbs-managment-service_log_2024120218.txt')
    
    # Получаем первую запись
    if parser.logs:
        first_log = parser.logs[0]
        
        print("Исходная строка из файла:")
        with open('Logs/cbs-managment-service_log_2024120218.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith("Summary data"):
                    print("-" * 80)
                    print(line.strip())
                    print("-" * 80)
                    values = line.strip().split(';')
                    print(f"\nКоличество значений в исходной строке: {len(values)}")
                    print("Значения:")
                    for i, v in enumerate(values):
                        if v.strip():
                            print(f"{i}: {v.strip()}")
                    break
        
        print("\nРезультат парсинга:")
        print("-" * 80)
        
        # Выводим все значения с их длинами
        for key, value in first_log.items():
            if value:  # Выводим только непустые значения
                print(f"{key}:")
                print(f"Значение: {value}")
                print(f"Длина: {len(str(value))}")
                print("-" * 80)
        
        # Создаем тестовый файл с одной строкой
        with open('test_output.txt', 'w', encoding='utf-8') as f:
            # Записываем значения в том же порядке, что и в columns
            values = [str(first_log.get(col, '')) for col in parser.columns]
            line = ';'.join(values)
            f.write(line)
        
        print("\nСоздан файл test_output.txt с первой валидной строкой")
        print(f"Количество столбцов в строке: {len(values)}")
        print(f"Общая длина строки: {len(line)}")
    else:
        print("Не удалось загрузить данные из лог-файла")

if __name__ == '__main__':
    test_single_line() 