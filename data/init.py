"""Подключение к SQLite, схема таблиц и стартовые данные."""
import sqlite3

from config import settings

DB_PATH = settings.db

# Одно соединение на всё приложение. check_same_thread=False нужен, потому что
# обычные def-эндпоинты FastAPI выполняет в разных потоках.
# ponytail: одно соединение без пула; для настоящей нагрузки нужен пул (SQLAlchemy) и Postgres.
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row  # строки читаются как словари: row["name"]

SCHEMA = """
create table if not exists creature (
    name        text primary key,
    country     text not null,
    area        text not null default '',
    description text not null default '',
    aka         text not null default ''
);
create table if not exists explorer (
    name        text primary key,
    country     text not null,
    description text not null default ''
);
create table if not exists user (
    name text primary key,
    hash text not null
);
"""

SEED_CREATURES = [
    ("Yeti", "CN", "Himalayas", "Hirsute Himalayan", "Abominable Snowman"),
    ("Bigfoot", "US", "*", "Yeti's Cousin Eddie", "Sasquatch"),
]
SEED_EXPLORERS = [
    ("Claude Hande", "FR", "Scarce during full moons"),
    ("Noah Weiser", "DE", "Myopic machete man"),
]


def init_db() -> None:
    """Создаёт таблицы и заполняет пустые таблицы стартовыми данными."""
    conn.executescript(SCHEMA)
    with conn:  # with conn = транзакция: commit при успехе, rollback при ошибке
        if conn.execute("select count(*) from creature").fetchone()[0] == 0:
            conn.executemany("insert into creature values (?, ?, ?, ?, ?)", SEED_CREATURES)
        if conn.execute("select count(*) from explorer").fetchone()[0] == 0:
            conn.executemany("insert into explorer values (?, ?, ?)", SEED_EXPLORERS)
