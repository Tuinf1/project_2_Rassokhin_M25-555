from typing import Any

from src.primitive_db.utils import DATA_DIR, METADATA_PATH, save_metadata

SUPPORTED_TYPES: set[str] = {"int", "str", "bool"}


def create_table(
    metadata: dict[str, Any],
    table_name: str,
    columns: list[str]
) -> dict[str, Any]:
    """
    Создаёт таблицу в метаданных.

    metadata структура:
    {
      "tables": {
         "users": {
            "columns": {"ID": "int", "name": "str", ...}
         }
      }
    }

    columns: ["name:str", "age:int", "is_active:bool"]
    """

    if not isinstance(metadata, dict):
        raise TypeError("metadata должен быть dict.")

    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("table_name должен быть непустой строкой.")

    if not isinstance(columns, list):
        raise TypeError("columns должен быть list[str].")

    # 1) инициализация структуры
    if "tables" not in metadata:
        metadata["tables"] = {}

    if not isinstance(metadata["tables"], dict):
        raise TypeError('metadata["tables"] должен быть dict.')

    tables: dict[str, Any] = metadata["tables"]

    # 2) проверка существования таблицы
    if table_name in tables:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    # 3) собираем колонки (с автодобавлением ID:int)
    table_columns: dict[str, str] = {"ID": "int"}

    # 4) парсинг и проверка столбцов
    for raw in columns:
        if not isinstance(raw, str):
            raise TypeError("Каждый элемент columns должен быть \
                            строкой вида 'name:type'.")

        item = raw.strip()
        if ":" not in item:
            raise ValueError(f'Некорректное значение: \
                             "{raw}". Ожидается формат "name:type".')

        name, col_type = item.split(":", 1)
        name = name.strip()
        col_type = col_type.strip()

        if not name:
            raise ValueError(f'Некорректное имя столбца в "{raw}".')

        if name == "ID":
            raise ValueError('Столбец "ID" добавляется автоматически. ' \
            'Не передавайте его в columns.')

        if name in table_columns:
            raise ValueError(f'Дублирование столбца "{name}".')

        if col_type not in SUPPORTED_TYPES:
            raise ValueError(
                f'Некорректный тип "{col_type}" для столбца "{name}". '
                f"Разрешены только: {sorted(SUPPORTED_TYPES)}."
            )

        table_columns[name] = col_type

    # 5) запись в метаданные
    tables[table_name] = {"columns": table_columns}

    return metadata


def drop_table(metadata: dict[str, Any], table_name: str) -> dict[str, Any]:
    """
    Удаляет таблицу из метаданных.

    Ожидаемая структура:
    metadata = {
      "tables": {
        "users": {"columns": {...}},
        ...
      }
    }
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    metadata_path = METADATA_PATH

    if not isinstance(metadata, dict):
        raise TypeError("metadata должен быть dict.")

    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("table_name должен быть непустой строкой.")

    # гарантируем ключ tables (как и в create_table)
    if "tables" not in metadata:
        metadata["tables"] = {}

    if not isinstance(metadata["tables"], dict):
        raise TypeError('metadata["tables"] должен быть dict.')

    tables: dict[str, Any] = metadata["tables"]

    if table_name not in tables:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    del tables[table_name]
    save_metadata(metadata_path, metadata)
    return metadata

