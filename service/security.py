"""Хеширование паролей и JWT-токены на чистой стандартной библиотеке."""
import base64
import hashlib
import hmac
import json
import os
import time

from config import settings

SECRET = settings.secret
TOKEN_MINUTES = settings.token_minutes

# ---------- Пароли ----------
# scrypt специально медленный и жрёт память: перебирать пароли по украденной базе дорого.
# Соль (16 случайных байт) делает хеши одинаковых паролей разными.
SCRYPT_PARAMS = {"n": 2**14, "r": 8, "p": 1}


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, **SCRYPT_PARAMS)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    _, salt_hex, digest_hex = stored.split("$")
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), **SCRYPT_PARAMS)
    # compare_digest сравнивает за одинаковое время, чтобы по скорости ответа ничего не угадать.
    return hmac.compare_digest(digest.hex(), digest_hex)


# ---------- JWT (HS256) ----------
# Токен = base64(header).base64(payload).base64(подпись). Данные НЕ шифруются, только подписываются:
# прочитать payload может кто угодно, а подделать без SECRET нельзя.
# ponytail: самописный JWT ради понимания; в боевом проекте бери библиотеку PyJWT.


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _sign(message: str) -> str:
    return _b64encode(hmac.new(SECRET.encode(), message.encode(), hashlib.sha256).digest())


def create_token(name: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": name, "exp": int(time.time()) + TOKEN_MINUTES * 60}
    message = f"{_b64encode(json.dumps(header).encode())}.{_b64encode(json.dumps(payload).encode())}"
    return f"{message}.{_sign(message)}"


def decode_token(token: str) -> str | None:
    """Возвращает имя пользователя или None, если токен битый, поддельный или просрочен."""
    try:
        header_b64, payload_b64, signature = token.split(".")
        expected = _sign(f"{header_b64}.{payload_b64}")
        if not hmac.compare_digest(signature.encode(), expected.encode()):
            return None
        payload = json.loads(_b64decode(payload_b64))
    except ValueError:  # кривой формат, base64 или JSON
        return None
    if not isinstance(payload, dict) or payload.get("exp", 0) < time.time():
        return None
    return payload.get("sub")
