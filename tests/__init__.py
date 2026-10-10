import os

# Тесты работают с базой в памяти, а не с cryptid.db.
# Этот файл импортируется раньше тестов, поэтому переменная задаётся ДО импорта приложения.
os.environ["CRYPTID_DB"] = ":memory:"
os.environ["CRYPTID_LOG_LEVEL"] = "WARNING"  # чтобы логи не засоряли вывод тестов

from data.init import conn, init_db  # noqa: E402


def reset_db() -> None:
    """Пересоздаёт таблицы со стартовыми данными, чтобы тесты не влияли друг на друга."""
    conn.executescript(
        "drop table if exists creature; drop table if exists explorer; drop table if exists user;"
    )
    init_db()


def auth_headers(client, name: str = "tester", password: str = "secret-pass") -> dict:
    """Регистрирует пользователя, логинится и отдаёт заголовок с токеном."""
    client.post("/users", json={"name": name, "password": password})
    token = client.post("/users/token", data={"username": name, "password": password}).json()
    return {"Authorization": f"Bearer {token['access_token']}"}
