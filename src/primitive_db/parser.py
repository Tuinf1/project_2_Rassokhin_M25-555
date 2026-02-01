def _auto_cast(value):
    """
    Преобразует строку в int / bool / str
    """
    value = value.strip()

    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        return value.strip('"').strip("'")


# =========================
# WHERE
# =========================

def parse_where(expr):
    """
    'age = 28'        -> {'age': 28}
    'name = "Alice"' -> {'name': 'Alice'}
    """

    if "=" not in expr:
        raise ValueError("Ожидается условие вида: column = value")

    column, value = expr.split("=", 1)

    column = column.strip()
    value = value.strip()

    if not column:
        raise ValueError("Имя столбца не может быть пустым")

    return {column: _auto_cast(value)}


# =========================
# SET
# =========================

def parse_set(expr):
    """
    'age = 30'        -> {'age': 30}
    'name = "Bob"'   -> {'name': 'Bob'}
    """

    return parse_where(expr)