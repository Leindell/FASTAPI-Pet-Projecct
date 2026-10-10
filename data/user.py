import sqlite3

from errors import Duplicate, Missing
from model.user import UserInDB

from .init import conn


def get_one(name: str) -> UserInDB:
    row = conn.execute("select * from user where name = :name", {"name": name}).fetchone()
    if row is None:
        raise Missing(f"Пользователь {name} не найден")
    return UserInDB(**dict(row))


def create(user: UserInDB) -> UserInDB:
    try:
        with conn:
            conn.execute("insert into user (name, hash) values (:name, :hash)", user.model_dump())
    except sqlite3.IntegrityError:
        raise Duplicate(f"Пользователь {user.name} уже есть") from None
    return user
