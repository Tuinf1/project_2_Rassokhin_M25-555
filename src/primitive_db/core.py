from typing import Any
# from src.primitive_db.utils import METADATA_PATH, save_metadata,
import json
from src.primitive_db.utils import DATA_DIR, load_table_data, save_table_data

SUPPORTED_TYPES = {
    "int": int,
    "str": str,
    "bool": bool,
}

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


def select(table_data, where_clause=None):
    rows = table_data["rows"]

    if where_clause is None:
        return rows.copy()

    result = []
    for row in rows:
        ok = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                ok = False
                break
        if ok:
            result.append(row)

    return result

def info_table(table_name: str) -> None:
    if not table_name or not table_name.strip():
        raise ValueError("Имя таблицы должно быть непустым.")

    table_file = DATA_DIR / f"{table_name}.json"
    if not table_file.exists():
        raise ValueError(f'Таблица "{table_name}" не существует.')

    try:
        with table_file.open("r", encoding="utf-8") as f:
            table_data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Файл {table_file} повреждён.") from exc

    if not isinstance(table_data, dict):
        raise ValueError("Некорректная структура таблицы.")

    columns = table_data.get("columns")
    rows = table_data.get("rows")

    if not isinstance(columns, dict) or not isinstance(rows, list):
        raise ValueError("Некорректная структура таблицы.")

    print(f"Таблица: {table_name}")
    print("Столбцы:")
    for name, typ in columns.items():
        print(f"  - {name}: {typ}")

    print(f"Количество строк: {len(rows)}")

def delete(table_data, where_clause):
    rows = table_data["rows"]
    remaining = []
    deleted = []

    for row in rows:
        ok = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                ok = False
                break

        if ok:
            deleted.append(row)
        else:
            remaining.append(row)

    table_data["rows"] = remaining
    return deleted



def update(table_data, set_clause, where_clause):
    rows = table_data["rows"]
    updated = []

    for row in rows:
        ok = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                ok = False
                break

        if ok:
            for set_key, set_value in set_clause.items():
                if set_key == "ID":
                    raise ValueError("ID изменять нельзя")
                row[set_key] = set_value

            updated.append(row)

    return updated




def insert(metadata, table_name, values):
    # 1. Проверка существования таблицы
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    table_schema = metadata[table_name]["columns"]
    column_names = list(table_schema.keys())

    if column_names[0] != "ID":
        raise ValueError("Первый столбец должен быть ID")

    expected_count = len(column_names) - 1
    if len(values) != expected_count:
        raise ValueError(
            f"Ожидалось {expected_count} значений, получено {len(values)}"
        )

    # 2. Загрузка данных таблицы
    table_data = load_table_data(table_name)
    rows = table_data["rows"]

    # 3. Генерация нового ID
    if rows:
        new_id = max(row["ID"] for row in rows) + 1
    else:
        new_id = 1

    # 4. Валидация типов и сбор записи
    new_row = {"ID": new_id}

    for value, col_name in zip(values, column_names[1:]):
        expected_type_name = table_schema[col_name]
        expected_type = SUPPORTED_TYPES[expected_type_name]

        if not isinstance(value, expected_type):
            raise TypeError(
                f'Поле "{col_name}" ожидает {expected_type_name}, '
                f"получено {type(value).name}"
            )

        new_row[col_name] = value

    # 5. Добавление строки
    rows.append(new_row)

    # 6. СОХРАНЕНИЕ В JSON ПРЯМО ТУТ
    save_table_data(table_name, table_data)

    return new_row