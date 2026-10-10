"""Сервисный слой: бизнес-логика. Не знает ни про HTTP, ни про то, где лежат данные."""
import data.creature as data
from errors import Invalid
from model.creature import Creature, CreatureUpdate


def get_all(country: str | None = None, limit: int = 20, offset: int = 0) -> list[Creature]:
    return data.get_all(country, limit, offset)


def get_one(name: str) -> Creature:
    return data.get_one(name)


def create(creature: Creature) -> Creature:
    # Пример бизнес-правила: прозвище не должно повторять имя.
    if creature.aka.lower() == creature.name.lower():
        raise Invalid("aka не должно совпадать с name")
    return data.create(creature)


def modify(name: str, changes: CreatureUpdate) -> Creature:
    return data.modify(name, changes)


def delete(name: str) -> None:
    data.delete(name)
