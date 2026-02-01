import shlex

def parse_values(values_str: str, single: bool = False):
    """
    '"Sergei", 28, true' → ['Sergei', 28, True]
    "name='Bob'" (single=True) → ('name', 'Bob')
    """
    values_str = values_str.strip()

    if single:
        if "=" not in values_str:
            raise ValueError("Ожидается выражение вида col=value")
        key, val = values_str.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        val = _auto_cast(val)
        return key, val

    parts = shlex.split(values_str)
    result = [_auto_cast(val) for val in parts]
    return result


def parse_condition(tokens: list[str]) -> dict:
    """
    ['id=5'] или ['name="Bob"'] → {'id': 5}
    """
    expr = " ".join(tokens).strip()
    if "=" not in expr:
        raise ValueError("Ожидается выражение col=value")
    key, val = expr.split("=", 1)
    key = key.strip()
    val = val.strip().strip('"').strip("'")
    return {key: _auto_cast(val)}


def _auto_cast(val: str):
    """
    Преобразует строку в int, bool или оставляет str
    """
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    try:
        return int(val)
    except ValueError:
        return val