import json
from src.primitive_db.utils import (
    load_table_data,
    save_table_data,
    DATA_DIR,
)
from src.primitive_db.parser import  parse_values

from src.primitive_db.core import  insert
# =========================
# HELP
# =========================

def _print_help():
    """Печать справки"""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> insert into <имя_таблицы> values (<значение1>, ...) - " +
      "добавить запись")
    print("<command> select from <имя_таблицы> [where <столбец>=<значение>] - " +
      "вывести записи")
    print("<command> update <имя_таблицы> set <столбец> = <значение> where <условие> -" +
      "обновить")
    print("<command> delete from <имя_таблицы> where <столбец>=<значение> -" +
      "удалить запись")
    print("<command> info <имя_таблицы> - информация о таблице")
    print("<command> exit - выйти")
    print("<command> help - справка\n")

# =========================
# LIST_TABLE
# =========================

def list_tables() -> None:
    """
    Показывает все таблицы (json-файлы в data/)
    """
    if not DATA_DIR.exists():
        print("Таблицы отсутствуют.")
        return

    tables = [
        file.stem
        for file in DATA_DIR.iterdir()
        if file.is_file() and file.suffix == ".json"
    ]

    if not tables:
        print("Таблицы отсутствуют.")
        return

    print("Список таблиц:")
    for name in sorted(tables):
        print(f"  - {name}")


# =========================
# CREATE_TABLE
# =========================

def create_table(table_name: str, columns_input: list[str]) -> None:
    if not table_name or not table_name.strip():
        raise ValueError("Имя таблицы должно быть непустым.")

    table_file = DATA_DIR / f"{table_name}.json"
    if table_file.exists():
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    valid_types = {"int", "str", "bool"}

    columns: dict[str, str] = {
        "ID": "int"
    }

    for col in columns_input:
        if ":" not in col:
            raise ValueError(
                f'Некорректное значение "{col}". Используйте формат name:type'
            )

        name, typ = col.split(":", 1)

        if not name.isidentifier():
            raise ValueError(f'Некорректное имя столбца: "{name}"')

        if typ not in valid_types:
            raise ValueError(
                f'Некорректный тип "{typ}". Допустимы: int, str, bool'
            )

        if name in columns:
            raise ValueError(f'Столбец "{name}" уже существует.')

        columns[name] = typ

    table_data = {
        "columns": columns,
        "rows": []
    }

    table_file.parent.mkdir(parents=True, exist_ok=True)
    table_file.write_text(
        json.dumps(table_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f'OK: таблица "{table_name}" создана')


# =========================
# DROP_TABLE
# =========================

def drop_table(table_name: str) -> None:
    """
    Удаляет таблицу (json-файл)
    """
    if not table_name or not table_name.strip():
        raise ValueError("Имя таблицы должно быть непустым.")

    table_file = DATA_DIR / f"{table_name}.json"
    if not table_file.exists():
        raise ValueError(f'Таблица "{table_name}" не существует.')

    table_file.unlink()
    print(f'OK: таблица "{table_name}" удалена')


# =========================
# WELCOME / CLI
# =========================

def run() -> None:
    print("Primitive DB запущена.")
    _print_help()

    while True:
        try:
            raw = input(">> ").strip()
            if not raw:
                continue

            tokens = raw.split()
            cmd = tokens[0]

            if cmd == "help":
                _print_help()

            elif cmd == "list_tables":
                list_tables()
            

            elif raw.lower().startswith("insert into"):
                try:
                    before_values, values_part = raw.split("values", 1)
                except ValueError:
                    raise ValueError(
                        "Использование: insert into <table> values (<v1>, <v2>, ...)"
                    )

                tokens_before = before_values.strip().split()

                if len(tokens_before) != 3 or tokens_before[1] != "into":
                    raise ValueError(
                        "Использование: insert into <table> values (...)")

                table_name = tokens_before[2]

                values_part = values_part.strip()
                if not (values_part.startswith("(") and values_part.endswith(")")):
                    raise ValueError("Значения должны быть в скобках (...)")

                values_str = values_part[1:-1]

                values = parse_values(values_str)

                table_data = load_table_data(table_name)

                row = insert(table_data, values)

                save_table_data(table_name, table_data)

                print("OK: добавлена запись:", row)


           


            elif cmd == "create_table":
                if len(tokens) < 3:
                    raise ValueError(
                        "Использование: create_table <table> name:type ..."
                    )

                table_name = tokens[1]
                columns_input = tokens[2:]

                create_table(table_name, columns_input)


            elif cmd == "drop_table":
                if len(tokens) != 2:
                    raise ValueError("Использование: drop_table <table>")
                drop_table(tokens[1])

            elif cmd == "exit":
                print("Выход.")
                break

            else:
                print(f"Неизвестная команда: {cmd}")

        except Exception as exc:
            print(f"Ошибка: {exc}")