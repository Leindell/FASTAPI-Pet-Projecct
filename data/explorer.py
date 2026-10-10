import sqlite3

from errors import Duplicate, Missing
from model.explorer import Explorer, ExplorerUpdate

from .init import conn


def row_to_model(row: sqlite3.Row) -> Explorer:
    return Explorer(**dict(row))


def get_all() -> list[Explorer]:
    return [row_to_model(row) for row in conn.execute("select * from explorer order by name")]


def get_one(name: str) -> Explorer:
    row = conn.execute("select * from explorer where name = :name", {"name": name}).fetchone()
    if row is None:
        raise Missing(f"Исследователь {name} не найден")
    return row_to_model(row)


def create(explorer: Explorer) -> Explorer:
    qry = """insert into explorer (name, country, description)
             values (:name, :country, :description)"""
    try:
        with conn:
            conn.execute(qry, explorer.model_dump())
    except sqlite3.IntegrityError:
        raise Duplicate(f"Исследователь {explorer.name} уже есть") from None
    return explorer


def modify(name: str, changes: ExplorerUpdate) -> Explorer:
    fields = changes.model_dump(exclude_none=True)
    if not fields:
        return get_one(name)
    assignments = ", ".join(f"{column} = :{column}" for column in fields)
    with conn:
        cursor = conn.execute(
            f"update explorer set {assignments} where name = :name", {**fields, "name": name}
        )
    if cursor.rowcount == 0:
        raise Missing(f"Исследователь {name} не найден")
    return get_one(name)


def delete(name: str) -> None:
    with conn:
        cursor = conn.execute("delete from explorer where name = :name", {"name": name})
    if cursor.rowcount == 0:
        raise Missing(f"Исследователь {name} не найден")
