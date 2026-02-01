import shlex


def parse_values(values_str):
    """'"Sergei", 28, true' -> ['Sergei', 28, True]"""
    parts = shlex.split(values_str)
    result = []

    for val in parts:
        if val.lower() == "true":
            result.append(True)
        elif val.lower() == "false":
            result.append(False)
        else:
            try:
                result.append(int(val))
            except ValueError:
                result.append(val)

    return result