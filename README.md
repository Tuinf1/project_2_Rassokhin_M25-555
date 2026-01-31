source .venv/bin/activate
make install
make project

poetry add prettytable

## 🎥 Демо работы приложения 1 часть version = "0.4.1"

В видео ниже показано:
- установка пакета
- запуск базы данных
- создание таблицы
- проверка
- удаление таблицы

[![asciinema demo](https://asciinema.org/a/wTaXfkHWZUZmCst8)](https://asciinema.org/a/wTaXfkHWZUZmCst8)



## 📋 Управление таблицами

Программа поддерживает базовые команды управления таблицами через консольный интерфейс. Все таблицы сохраняются в файле db_meta.json.

---

### 🔧 Команды

| Команда                       | Назначение                            | Пример использования |
|-------------------------------|---------------------------------------|----------------------|
| create_table <имя> <колонки>  | Создать новую таблицу с колонками     | create_table users name:str age:int is_active:bool |
| drop_table <имя>              | Удалить существующую таблицу          | drop_table users     |
| list_tables                   | Показать список всех таблиц           | list_tables          |
| help                          | Справка по командам                   | help                 |
| exit                          | Выход из программы                    | exit                 |

---

### 📌 Допустимые типы данных колонок

- int — целое число  
- str — строка  
- bool — булев тип (True / False)

---

### ✅ Пример сценария работы

```bash
Введите команду: create_table users name:str age:int is_active:bool
OK: таблица "users" создана.

Введите команду: list_tables
Список таблиц:
1. users

Введите команду: drop_table users
OK: таблица "users" удалена.

Введите команду: list_tables
Нет ни одной таблицы.