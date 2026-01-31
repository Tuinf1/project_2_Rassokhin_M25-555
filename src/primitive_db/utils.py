import json
from pathlib import Path


# === Константы путей ===
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR
METADATA_FILENAME = "db_meta.json"
METADATA_PATH = DATA_DIR / METADATA_FILENAME


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
            
            return data
    except FileNotFoundError:
        return {}
    
    

def save_metadata(filepath: str, data: dict):
    """
    Сохраняет переданные данные в JSON-файл.
    """
    path = Path(filepath)
    
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)