import json
from pathlib import Path


def load_metadata(filepath: str):
    """
    Загружает данные из JSON-файла.
    Если файл не найден — возвращает пустой словарь {}.
    Использует try...except FileNotFoundError.
    """
    # определение пути файла json
    path = Path(filepath)

    # загрузка данных из json 
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    return data
    
def save_metadata(filepath: str, data: dict):
    """
    Сохраняет переданные данные в JSON-файл.
    """
    path = Path(filepath)
    
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)