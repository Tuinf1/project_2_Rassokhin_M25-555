from typing import Any

from src.primitive_db.utils import DATA_DIR, METADATA_PATH, save_metadata, load_table_data, save_table_data

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



def select(
    table_data,
    where_clause
):
    rows = table_data["rows"]

    if where_clause is None:
        return rows.copy()

    result: list[dict[str, Any]] = []

    for row in rows:
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break

        if match:
            result.append(row)

    return result


def delete(
    table_data,
    where_clause
):
    rows = table_data["rows"]
    remaining_rows: list[dict[str, Any]] = []
    deleted_rows: list[dict[str, Any]] = []

    for row in rows:
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break

        if match:
            deleted_rows.append(row)
        else:
            remaining_rows.append(row)

    table_data["rows"] = remaining_rows
    return deleted_rows

def update(
    table_data,
    set_clause,
    where_clause
):
    rows = table_data["rows"]
    updated_rows: list[dict[str, Any]] = []

    for row in rows:
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break

        if match:
            for set_key, set_value in set_clause.items():
                if set_key == "ID":
                    raise ValueError("ID нельзя изменять.")
                row[set_key] = set_value

            updated_rows.append(row)

    return updated_rows


def insert(
    metadata: dict[str, Any],
    table_name: str,
    values: list[Any],
):
    # 1. Проверка таблицы
    if table_name not in metadata.get("tables", {}):
        raise ValueError(f'Таблица "{table_name}" не существует.')

    table_meta = metadata["tables"][table_name]
    columns = table_meta["columns"]

    column_names = list(columns.keys())

    if column_names[0] != "ID":
        raise ValueError("Первый столбец должен быть ID.")

    expected_values_count = len(column_names) - 1

    # 2. Проверка количества значений (без ID)
    if len(values) != expected_values_count:
        raise ValueError(
            f"Ожидалось {expected_values_count} значений, получено {len(values)}."
        )

    # 3. Загрузка данных таблицы
    table_data = load_table_data(table_name)
    rows = table_data["rows"]

    # 4. Генерация нового ID
    if rows:
        max_id = max(row["ID"] for row in rows)
        new_id = max_id + 1
    else:
        new_id = 1

    # 5. Валидация типов и сбор записи
    new_row: dict[str, Any] = {"ID": new_id}

    for value, column_name in zip(values, column_names[1:]):
        expected_type_name = columns[column_name]
        expected_type = SUPPORTED_TYPES.get(expected_type_name)

        if expected_type is None:
            raise ValueError(f"Неподдерживаемый тип: {expected_type_name}")

        if not isinstance(value, expected_type):
            raise TypeError(
                f'Поле "{column_name}" ожидает {expected_type_name}, '
                f"получено {type(value).name}"
            )

        new_row[column_name] = value

    # 6. Добавление и сохранение
    rows.append(new_row)
    save_table_data(table_name, table_data)

    return new_row