from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """То, что присылают при регистрации."""

    name: str = Field(min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=128)


class User(BaseModel):
    """То, что видит клиент. Хеша здесь нет и быть не должно."""

    name: str


class UserInDB(User):
    """То, что лежит в базе: пользователь + хеш пароля."""

    hash: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
