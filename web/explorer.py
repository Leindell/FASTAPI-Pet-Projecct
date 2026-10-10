from fastapi import APIRouter, Depends, status

import service.explorer as service
from model.explorer import Explorer, ExplorerUpdate
from web.deps import get_current_user

router = APIRouter(prefix="/explorers", tags=["explorers"])


@router.get("")
def get_all() -> list[Explorer]:
    return service.get_all()


@router.get("/{name}")
def get_one(name: str) -> Explorer:
    return service.get_one(name)


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def create(explorer: Explorer) -> Explorer:
    return service.create(explorer)


@router.patch("/{name}", dependencies=[Depends(get_current_user)])
def modify(name: str, changes: ExplorerUpdate) -> Explorer:
    return service.modify(name, changes)


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
def delete(name: str) -> None:
    service.delete(name)
