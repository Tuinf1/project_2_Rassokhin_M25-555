source .venv/bin/activate
make install
make project

Primitive DB — это учебная embedded-база данных, реализованная на Python.
Данные хранятся локально в виде JSON-файлов, управление осуществляется
через интерактивный CLI.

Проект предназначен для изучения:
- архитектуры CLI-приложений
- принципов CRUD-операций
- работы с файловыми хранилищами
- базовой валидации схем и типов данных


## 🎥 Демо работы приложения 1 часть version 

В видео ниже показано:
- установка пакета
- запуск базы данных
- создание таблицы
- проверка
- удаление таблицы

[![asciinema demo](https://asciinema.org/a/wTaXfkHWZUZmCst8)](https://asciinema.org/a/wTaXfkHWZUZmCst8)


## 🎥 Демо работы приложения 2 часть

В видео ниже показано:
- установка пакета
- запуск базы данных
- создание таблицы
- вывод информации о таблице
- вставка данных
- вывод таблицы
- вывод списка таблицы
- удаление таблицы

[![asciinema demo](https://asciinema.org/a/2dSwoSPevs16HmcK)](https://asciinema.org/a/2dSwoSPevs16HmcK)


## 🎥 Демо работы приложения 3 часть

В видео ниже показано:
    автоматическая обработка ошибок при выполнении команд (@handle_db_errors)
    запрос подтверждения перед удалением таблицы (@confirm_action)
    измерение времени выполнения операций (@log_time)
    кеширование результатов SELECT-запросов (create_cacher)

[![asciinema demo](https://asciinema.org/a/bxxYMkGYUufHvhtd)](https://asciinema.org/a/bxxYMkGYUufHvhtd)


## 📋 Управление таблицами

Программа поддерживает базовые команды управления таблицами через консольный интерфейс. Все таблицы сохраняются в файле db_meta.json.

---

### 🔧 Команды

---

## 🔧 Команды

| Команда                      | Назначение                                                             | Пример использования |
|------------------------------|------------|-----------------------------------------------------------|
| create_table <имя> name:type | Создать новую таблицу с заданной схемой (ID добавляется автоматически) | create_table users name:str age:int is_active:bool |
| drop_table <имя>             | Удалить существующую таблицу                                           | drop_table users |
| list_table                   | Показать список всех таблиц                                            | list_tables |
| info <имя>                   | Показать информацию о таблице (схема, количество строк)                | info users |
| insert into <имя> column=value... | Добавить строку в таблицу (без указания ID)                       | insert into users name=Ivan age=30 is_active=true |
|                                                                                                       | insert into users values ("Sergei", 28, true)|
|delete from <имя табл> where column=value    | удалить строку по столбцу и значению                              | delete from users where age = 28
|select from <наименование таблицы> where <имя столбца>=<значение> | выводит строки из таблицы по заданному значению| select from users where age = 25 |
| help                         | Показать справку по командам                                           | help |
| exit                         | Выход из программы                                                     | exit |

---

### 📌 Допустимые типы данных колонок

- int — целое число  
- str — строка  
- bool — булев тип (True / False)

---

### ✅ Пример сценария работы

---

## ✅ Пример сценария работы

```bash
Введите команду: create_table users name:str age:int is_active:bool
OK: таблица "users" создана.

Введите команду: list_table
Список таблиц:
  - users

Введите команду: info users
Таблица: users
Столбцы:
  - ID: int
  - name: str
  - age: int
  - is_active: bool
Количество строк: 0

Введите команду: insert users name=Ivan age=30 is_active=true
OK: добавлена строка с ID=1

Введите команду: insert users name=Oleg age=25 is_active=false
OK: добавлена строка с ID=2

Введите команду: info users
Таблица: users
Столбцы:
  - ID: int
  - name: str
  - age: int
  - is_active: bool
Количество строк: 2

Введите команду: drop_table users
OK: таблица "users" удалена.

Введите команду: list_table
Таблицы отсутствуют.



### ✅ Обработка ошибок
Добавлен декоратор @handle_db_errors, который:
- перехватывает типичные ошибки (FileNotFoundError, KeyError, ValueError, TypeError);
- выводит понятные сообщения пользователю;
- избавляет от необходимости писать try...except в каждой функции.

Пример:
```python
@handle_db_errors
def select(...):
    ...

Добавлен декоратор @confirm_action("описание действия"), который:

спрашивает подтверждение у пользователя перед выполнением операций drop_table, delete;

операция отменяется, если пользователь вводит не y.

Пример:

@confirm_action("удаление таблицы")
def drop_table(...):
    ...