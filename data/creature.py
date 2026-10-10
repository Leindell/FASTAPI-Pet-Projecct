import sqlite3

from errors import Duplicate, Missing
from model.creature import Creature, CreatureUpdate

from .init import conn


def row_to_model(row: sqlite3.Row) -> Creature:
    return Creature(**dict(row))


def get_all(country: str | None = None, limit: int = 20, offset: int = 0) -> list[Creature]:
    qry = "select * from creature"
    params: dict = {"limit": limit, "offset": offset}
    if country is not None:
        qry += " where country = :country"
        params["country"] = country
    qry += " order by name limit :limit offset :offset"
    return [row_to_model(row) for row in conn.execute(qry, params)]


def get_one(name: str) -> Creature:
    # Значения передаём ТОЛЬКО через параметры (:name), никогда f-строкой: это защита от SQL-инъекций.
    row = conn.execute("select * from creature where name = :name", {"name": name}).fetchone()
    if row is None:
        raise Missing(f"Существо {name} не найдено")
    return row_to_model(row)


def create(creature: Creature) -> Creature:
    qry = """insert into creature (name, country, area, description, aka)
             values (:name, :country, :area, :description, :aka)"""
    try:
        with conn:
            conn.execute(qry, creature.model_dump())
    except sqlite3.IntegrityError:
        raise Duplicate(f"Существо {creature.name} уже есть") from None
    return creature


def modify(name: str, changes: CreatureUpdate) -> Creature:
    fields = changes.model_dump(exclude_none=True)
    if not fields:
        return get_one(name)
    # Имена колонок берутся из полей модели, а не от клиента, поэтому f-строка тут безопасна.
    assignments = ", ".join(f"{column} = :{column}" for column in fields)
    with conn:
        cursor = conn.execute(
            f"update creature set {assignments} where name = :name", {**fields, "name": name}
        )
    if cursor.rowcount == 0:
        raise Missing(f"Существо {name} не найдено")
    return get_one(name)


def delete(name: str) -> None:
    with conn:
        cursor = conn.execute("delete from creature where name = :name", {"name": name})
    if cursor.rowcount == 0:
        raise Missing(f"Существо {name} не найдено")
