import json

from prettytable import PrettyTable

from src.primitive_db.core import delete, info_table, insert, select, update, list_tables, create_table, _print_help
from src.primitive_db.parser import parse_set, parse_where
from src.primitive_db.utils import (
    DATA_DIR,
    load_table_data,
    save_table_data,
)

from src.decorators import handle_db_errors, confirm_action, create_cacher

cache_select = create_cacher()




@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(table_name):
    table_file = DATA_DIR / f"{table_name}.json"

    # KeyError / FileNotFoundError перехватит декоратор
    table_file.unlink()

    print(f'OK: таблица "{table_name}" удалена')


# =========================
# CLI
# =========================

def run():
    print("Primitive DB запущена.")
    _print_help()

    while True:
        try:
            raw = input(">> ").strip()
            if not raw:
                continue

            tokens = raw.split()
            cmd = tokens[0].lower()

            # ---------- EXIT ----------
            if cmd == "exit":
                print("Выход.")
                break

            # ---------- HELP ----------
            elif cmd == "help":
                _print_help()

            # ---------- LIST ----------
            elif cmd == "list_tables":
                list_tables()

            # ---------- CREATE ----------
            elif cmd == "create_table":
                if len(tokens) < 3:
                    raise ValueError("create_table <table> col:type ...")

                create_table(tokens[1], tokens[2:])

            # ---------- DROP ----------
            elif cmd == "drop_table":
                if len(tokens) != 2:
                    raise ValueError("drop_table <table>")
                drop_table(tokens[1])


            elif cmd == "info":
                if len(tokens) != 2:
                    raise ValueError("Использование: info <table>")
                info_table(tokens[1])

            # ---------- INSERT ----------
            elif raw.lower().startswith("insert"):
                tokens = raw.strip().split()

                if len(tokens) < 3:
                    raise ValueError("Формат: insert [into] <table>" \
                    "values (...) или column=value ...")

                # 1. Определяем имя таблицы
                if tokens[1].lower() == "into":
                    table_name = tokens[2]
                    args = tokens[3:]
                else:
                    table_name = tokens[1]
                    args = tokens[2:]

                if not args:
                    raise ValueError("Не заданы значения для вставки")

                # 2. Ветка 1: insert ... values (...)
                if args[0].lower() == "values":
                    values_part = " ".join(args[1:]).strip()

                    if values_part.startswith("(") and values_part.endswith(")"):
                        values_part = values_part[1:-1]
                        raw_values = [v.strip() for v in values_part.split(",")]
                    else:
                        raw_values = values_part.split()

                    values = []
                    for v in raw_values:
                        if v.lower() == "true":
                            values.append(True)
                        elif v.lower() == "false":
                            values.append(False)
                        else:
                            try:
                                values.append(int(v))
                            except ValueError:
                                values.append(v.strip('"').strip("'"))

                    table_data = load_table_data(table_name)
                    metadata = {table_name: {"columns": table_data["columns"]}}
                    row = insert(metadata, table_name, values)
                    print("OK: добавлена запись:", row)

                # 3. Ветка 2: insert ... column=value ...
                else:
                    # Парсим column=value
                    kv_pairs = {}
                    for arg in args:
                        if "=" not in arg:
                            raise ValueError(f"Неверный \
                                             формат: {arg}. Используйте key=value")

                        key, val = arg.split("=", 1)
                        key = key.strip()
                        val = val.strip()

                        if not key:
                            raise ValueError("Имя поля не может быть пустым")

                        # авто-каст
                        if val.lower() == "true":
                            kv_pairs[key] = True
                        elif val.lower() == "false":
                            kv_pairs[key] = False
                        else:
                            try:
                                kv_pairs[key] = int(val)
                            except ValueError:
                                kv_pairs[key] = val.strip('"').strip("'")

                    # Загрузка схемы и проверка порядка
                    table_data = load_table_data(table_name)
                    columns = table_data["columns"]
                    expected_columns = list(columns.keys())[1:]  # без ID

                    # Значения в нужном порядке
                    values = []
                    for col in expected_columns:
                        if col not in kv_pairs:
                            raise ValueError(f"Не передано \
                                             значение для колонки '{col}'")
                        values.append(kv_pairs[col])

                    metadata = {table_name: {"columns": columns}}
                    row = insert(metadata, table_name, values)
                    print("OK: добавлена запись:", row)








            # ---------- SELECT ----------
            elif cmd == "select":
                if tokens[1] != "from":
                    raise ValueError("select from <table>")

                table_name = tokens[2]
                table_data = load_table_data(table_name)
                



                condition = None
                if "where" in tokens:
                    where_expr = " ".join(tokens[tokens.index("where") + 1:])
                    condition = parse_where(where_expr)

                key = str(condition) if condition else "ALL"

                    # ❗️ единственный вызов select — через кэш
                rows = cache_select(
                    key,
                    lambda: select(table_data, condition)
                )

                # rows = select(table_data, condition)
                
                # result = cache_select(key, lambda: select(table_data, where_clause))
                
                if not rows:
                    print("Нет данных.")
                else:
                    table = PrettyTable()
                    table.field_names = rows[0].keys()

                    for row in rows:
                        table.add_row(row.values())

                    print(table)

                  


            # ---------- UPDATE ----------
            elif cmd == "update":
                table_name = tokens[1]

                set_idx = tokens.index("set")
                where_idx = tokens.index("where")

                set_expr = " ".join(tokens[set_idx + 1:where_idx])
                where_expr = " ".join(tokens[where_idx + 1:])

                set_clause = parse_set(set_expr)
                where_clause = parse_where(where_expr)

                table_data = load_table_data(table_name)
                updated = update(table_data, set_clause, where_clause)
                save_table_data(table_name, table_data)

                print(f"Обновлено записей: {len(updated)}")
            # ---------- DELETE ----------
            elif cmd == "delete":
                if tokens[1] != "from":
                    raise ValueError("Использование: delete " \
                    "from <table> where <условие>")

                table_name = tokens[2]

                if "where" not in tokens:
                    raise ValueError("Для delete обязательно условие where")

                where_idx = tokens.index("where")
                where_expr = " ".join(tokens[where_idx + 1:])
                where_clause = parse_where(where_expr)

                table_data = load_table_data(table_name)
                deleted = delete(table_data, where_clause)
                save_table_data(table_name, table_data)

                print(f"Удалено записей: {len(deleted)}")

        except Exception as exc:
            print(f"Ошибка: {exc}")