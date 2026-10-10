import data.user as data
from errors import Missing
from model.user import User, UserCreate, UserInDB
from service.security import decode_token, hash_password, verify_password

# Хеш-пустышка: проверяем пароль даже для несуществующего логина, чтобы ответ шёл
# одинаковое время и по скорости нельзя было понять, есть такой пользователь или нет.
DUMMY_HASH = hash_password("dummy-password")


def register(user: UserCreate) -> User:
    return data.create(UserInDB(name=user.name, hash=hash_password(user.password)))


def authenticate(name: str, password: str) -> User | None:
    try:
        user = data.get_one(name)
    except Missing:
        verify_password(password, DUMMY_HASH)
        return None
    return user if verify_password(password, user.hash) else None


def user_from_token(token: str) -> User | None:
    name = decode_token(token)
    if name is None:
        return None
    try:
        return data.get_one(name)
    except Missing:
        return None
