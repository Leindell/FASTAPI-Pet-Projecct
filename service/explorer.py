import data.explorer as data
from model.explorer import Explorer, ExplorerUpdate


def get_all() -> list[Explorer]:
    return data.get_all()


def get_one(name: str) -> Explorer:
    return data.get_one(name)


def create(explorer: Explorer) -> Explorer:
    return data.create(explorer)


def modify(name: str, changes: ExplorerUpdate) -> Explorer:
    return data.modify(name, changes)


def delete(name: str) -> None:
    data.delete(name)
