# Cryptid API

Учебный REST API на FastAPI про криптидов (Йети, Бигфут и компания) и их исследователей.
Сделан по книге Билла Любановича «FastAPI: веб-разработка на Python», с поправками под современные версии (Pydantic v2, `lifespan`, `Annotated`).

Из зависимостей только `fastapi[standard]`. JWT, хеширование паролей, настройки и тесты сделаны на стандартной библиотеке Python.

## Что внутри

- Слоистая архитектура: `web` (эндпоинты) → `service` (бизнес-логика) → `data` (SQLite), модели Pydantic в `model`.
- CRUD для существ и исследователей, пагинация и фильтр по стране через `Depends`.
- Доменные ошибки (`errors.py`), которые глобальные обработчики превращают в 404, 409 и 400.
- Регистрация, логин по OAuth2 password flow, JWT (HS256 на `hmac`), пароли на `hashlib.scrypt`.
- Запись (POST, PATCH, DELETE) только для залогиненных пользователей.
- Настройки из переменных окружения `CRYPTID_*`, CORS, middleware с логом и временем ответа, `/health`.
- 35 тестов на `unittest`, их же без изменений запускает pytest.

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate.bat        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py
```

Документация: http://127.0.0.1:8000/docs

## Тесты

```bash
python -m unittest -v
```

## Настройки

| Переменная | По умолчанию | Что это |
|------------|--------------|---------|
| `CRYPTID_DB` | `cryptid.db` | путь к файлу SQLite |
| `CRYPTID_SECRET` | `dev-secret-change-me` | секрет подписи JWT, в проде обязательно свой |
| `CRYPTID_TOKEN_MINUTES` | `30` | время жизни токена |
| `CRYPTID_CORS_ORIGINS` | `http://localhost:3000` | разрешённые домены через запятую |
| `CRYPTID_LOG_LEVEL` | `INFO` | уровень логов |

Сгенерировать секрет: `python -c "import secrets; print(secrets.token_hex(32))"`

## Эндпоинты

| Метод | Путь | Доступ |
|-------|------|--------|
| GET | `/creatures?limit=&offset=&country=` | все |
| GET | `/creatures/{name}` | все |
| POST, PATCH, DELETE | `/creatures`, `/creatures/{name}` | с токеном |
| GET | `/explorers`, `/explorers/{name}` | все |
| POST, PATCH, DELETE | `/explorers`, `/explorers/{name}` | с токеном |
| POST | `/users` | регистрация |
| POST | `/users/token` | логин (форма username + password) |
| GET | `/users/me` | с токеном |
| GET | `/health` | все |
