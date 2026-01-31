import shlex
from typing import Any

from src.primitive_db.core import create_table, drop_table 
from src.primitive_db.utils import (
    METADATA_PATH,
    DATA_DIR,
    load_metadata,
    save_metadata
)



def _print_banner() -> None:
    print("Первая попытка запустить проект!")
    print("***")


def _print_help() -> None:
    print("<command> help - справочная информация")
    print("<command> exit - выйти из программы")
    print()
    print("<command> create_table <table_name> <col:type> <col:type> ...")
    print("          допустимые типы: int, str, bool")
    print("          пример: create_table users name:str age:int is_active:bool")
    print()
    print("<command> drop_table <table_name>")
    print("          пример: drop_table users")


def _normalize_command(tokens: list[str]) -> str:
    if not tokens:
        return ""
    return tokens[0].strip().lower()


def _print_prompt() -> None:
    print("Введите команду: ", end="")


def run() -> None:
    """
    Запуск приложения:
    - приветствие
    - основной (игровой) цикл
    - парсинг команд
    Поддерживаемые команды:
    - help
    - exit
    - create_table
    - drop_table
    """

    _print_banner()
    _print_help()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    metadata_path = METADATA_PATH

    while True:
        # 1) Загружаем актуальные метаданные
        try:
            metadata: dict[str, Any] = load_metadata(metadata_path)
            if metadata is None:
                metadata = {}
        except Exception as exc:
            print(f"Ошибка чтения метаданных: {exc}")
            metadata = {}

        _print_prompt()

        raw = input()

        if raw.strip() == "":
            continue

        # 2) разбор введенной команды
        try:
            tokens = shlex.split(raw)
        except ValueError as exc:
            print(f"Ошибка ввода: {exc}")
            continue

        cmd = _normalize_command(tokens)
        args = tokens[1:]

        # 3) Команды
        if cmd in ("exit", "quit", "q"):
            break

        if cmd in ("help", "h", "?"):
            _print_help()
            continue

        if cmd == "create_table":
            if len(args) < 1:
                print("Ошибка: нужно имя таблицы. Пример: create_table users name:str age:int")
                continue

            table_name = args[0]
            columns = args[1:]

            try:
                metadata = create_table(metadata, table_name, columns)
            except Exception as exc:
                print(f"Ошибка: {exc}")
                continue

            try:
                save_metadata(metadata_path, metadata)
            except Exception as exc:
                print(f"Ошибка сохранения метаданных: {exc}")
                continue

            print(f'OK: таблица "{table_name}" создана.')
            continue

        if cmd == "drop_table":
            if len(args) != 1:
                print("Ошибка: нужно ровно 1 аргумент. Пример: drop_table users")
                continue

            table_name = args[0]

            try:
                metadata = drop_table(metadata, table_name)
            except Exception as exc:
                print(f"Ошибка: {exc}")
                continue

            try:
                save_metadata(metadata_path, metadata)
            except Exception as exc:
                print(f"Ошибка сохранения метаданных: {exc}")
                continue

            print(f'OK: таблица "{table_name}" удалена.')
            continue

        print(f"Неизвестная команда: {cmd!r} (ввод: {raw!r})")
        print("Подсказка: введите 'help'.")