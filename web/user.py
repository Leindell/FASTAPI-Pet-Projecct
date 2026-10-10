from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

import service.user as service
from model.user import Token, User, UserCreate
from service.security import create_token
from web.deps import CurrentUser

router = APIRouter(prefix="/users", tags=["users"])


# service.register возвращает UserInDB с хешем, но "-> User" отрежет всё лишнее из ответа.
@router.post("", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate) -> User:
    return service.register(user)


# Логин по стандарту OAuth2: username и password приходят формой, а не JSON.
# Именно этот эндпоинт дёргает кнопка Authorize в /docs.
@router.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = service.authenticate(form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_token(user.name))


@router.get("/me")
def me(user: CurrentUser) -> User:
    return user
