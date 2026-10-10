import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import DEFAULT_SECRET, settings
from data.init import init_db
from errors import Duplicate, Invalid, Missing
from web import creature, explorer, user


logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("cryptid")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # до yield: выполняется один раз при старте сервера
    logger.info("База: %s", settings.db)
    if settings.secret == DEFAULT_SECRET:
        logger.warning("CRYPTID_SECRET не задан, используется секрет для разработки!")
    yield
    # после yield: выполняется при остановке (закрыть соединения, клиенты и т.п.)


app = FastAPI(title="Cryptid API", lifespan=lifespan)
app.include_router(creature.router)
app.include_router(explorer.router)
app.include_router(user.router)

# CORS: каким сайтам (фронтендам с других доменов) браузер разрешит ходить в наш API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware оборачивает КАЖДЫЙ запрос: код до call_next выполняется до эндпоинта, после него — после.
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
    logger.info("%s %s -> %s (%.1f мс)", request.method, request.url.path, response.status_code, elapsed_ms)
    return response


# Одно место, где ошибки предметной области превращаются в HTTP-коды.
@app.exception_handler(Missing)
def missing_handler(request: Request, exc: Missing) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(Duplicate)
def duplicate_handler(request: Request, exc: Duplicate) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(Invalid)
def invalid_handler(request: Request, exc: Invalid) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/")
def root():
    return {"message": "Криптиды на связи"}


# Health-check: его дёргают мониторинг и балансировщики, чтобы понять, что сервис жив.
@app.get("/health")
def health():
    return {"status": "ok"}
