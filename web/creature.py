from fastapi import APIRouter, Depends, status

import service.creature as service
from model.creature import Creature, CreatureUpdate
from web.deps import PageDep, get_current_user

router = APIRouter(prefix="/creatures", tags=["creatures"])

# Читать могут все, а создавать, менять и удалять только залогиненные: dependencies=[...].


@router.get("")
def get_all(page: PageDep, country: str | None = None) -> list[Creature]:
    return service.get_all(country, page.limit, page.offset)


@router.get("/{name}")
def get_one(name: str) -> Creature:
    return service.get_one(name)


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def create(creature: Creature) -> Creature:
    return service.create(creature)


@router.patch("/{name}", dependencies=[Depends(get_current_user)])
def modify(name: str, changes: CreatureUpdate) -> Creature:
    return service.modify(name, changes)


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
def delete(name: str) -> None:
    service.delete(name)
