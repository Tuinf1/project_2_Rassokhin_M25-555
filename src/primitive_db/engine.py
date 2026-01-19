

def _print_banner() -> None:
    print("Первая попытка запустить проект!")
    print("***")

def _print_help() -> None:
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

def _normalize_command(tokens: list[str]) -> str:
    if not tokens:
        return ""
    return tokens[0].strip().lower()


def _print_prompt() -> None:
    # Важно: оставляем формат как на примере
    print("Введите команду: ", end="")

def welcome() -> None:
    """
    Запуск приложения:
    - приветствие
    - основной (игровой) цикл
    - парсинг команд
    Поддерживаемые команды:
    - help
    - exit
    """
    _print_banner()
    _print_help()

    while True:
        _print_prompt()
        raw = input()

        # Пустая строка -> просто повторяем ввод
        if raw.strip() == "":
            continue

        tokens = raw.split()
        cmd = _normalize_command(tokens)


        if cmd in ("exit", "quit", "q"):
            # По условию ключевая команда exit
            break

        if cmd in ("help", "h", "?"):
            _print_help()
            continue

        
        print(f"Неизвестная команда: {cmd!r} (ввод: {raw!r})")

        #print(f"Подсказка: введите 'help'. Время обработки: {elapsed_ms:.2f} ms")