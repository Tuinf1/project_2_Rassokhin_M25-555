import json
from pathlib import Path

# Константы путей
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(BASE_DIR)
DATA_DIR = BASE_DIR / 'data'
# METADATA_FILENAME = "db_meta.json"
# METADATA_PATH = DATA_DIR / METADATA_FILENAME


# def load_metadata(filepath: str):
#     """
#     Загружает данные из JSON-файла.
#     Если файл не найден — возвращает пустой словарь {}.
#     Использует try...except FileNotFoundError.
#     """
#     # определение пути файла json
#     path = Path(filepath)
# # 
#     # загрузка данных из json 
#     try:
        
#         with path.open("r", encoding="utf-8") as f:
#             data = json.load(f)
            
#             return data
#     except FileNotFoundError:
#         return {}
    
    

# def save_metadata(filepath: str, data: dict):
#     """
#     Сохраняет переданные данные в JSON-файл.
#     """
#     path = Path(filepath)
    
#     with path.open("w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)


def load_table_data(table_name):
    """
    Загружает данные таблицы из data/<table_name>.json
    """

    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("table_name должен быть непустой строкой.")

    file_path = DATA_DIR / f"{table_name}.json"

    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Файл {file_path} повреждён.") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Некорректная структура данных в {file_path}.")

    return data


def save_table_data(table_name, data):
    """
    Сохраняет данные таблицы в data/<table_name>.json
    """

    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("table_name должен быть непустой строкой.")

    if not isinstance(data, dict):
        raise TypeError("data должна быть dict.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_path = DATA_DIR / f"{table_name}.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)