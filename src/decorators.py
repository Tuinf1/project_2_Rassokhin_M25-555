# src/decorators.py


import time
from functools import wraps


def handle_db_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: файл данных не найден.")
        except KeyError as e:
            print(f"Ошибка: ключ или таблица {e} не найдена.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except TypeError as e:
            print(f"Ошибка типа: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
    return wrapper


def confirm_action(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if answer.lower() == 'y':
                return func(*args, **kwargs)
            print("Операция отменена.")
        return wrapper
    return decorator



def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start
        print(f'\n⚙️ Функция "{func.__name__}" выполнилась за {duration:.10f} секунд.')
        return result
    return wrapper


def create_cacher():
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            print("Кэш: результат найден")
            return cache[key]
        print("\nКэш: нет результата, вызываю функцию...")
        result = value_func()
        cache[key] = result
        return result

    return cache_result