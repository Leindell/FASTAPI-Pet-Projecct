"""Общие зависимости веб-слоя. FastAPI вызывает их сам перед вызовом эндпоинта."""
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer

import service.user as user_service
from model.user import User


@dataclass
class Page:
    limit: int
    offset: int


def pagination(
    limit: Annotated[int, Query(ge=1, le=100, description="Сколько записей вернуть")] = 20,
    offset: Annotated[int, Query(ge=0, description="Сколько записей пропустить")] = 0,
) -> Page:
    return Page(limit, offset)


# Готовый тип: пишешь page: PageDep в любом эндпоинте, и пагинация подключена.
PageDep = Annotated[Page, Depends(pagination)]

# Достаёт токен из заголовка "Authorization: Bearer <токен>". Нет заголовка — сразу 401.
# tokenUrl говорит /docs, куда слать логин и пароль.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


# Зависимость от зависимости: FastAPI сначала вызовет oauth2_scheme, потом эту функцию.
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    user = user_service.user_from_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен невалидный или просрочен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
