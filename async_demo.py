import asyncio
import time

from fastapi import FastAPI

app = FastAPI(title="async demo")


# Обычный def: FastAPI запускает его в пуле потоков, блокировка никому не мешает.
@app.get("/sleep/sync")
def sleep_sync():
    time.sleep(1)
    return "sync: поспал 1 c"


# async def + await: пока ждём, event loop обслуживает другие запросы.
@app.get("/sleep/async")
async def sleep_async():
    await asyncio.sleep(1)
    return "async: поспал 1 c"


# Ошибка новичка: async def + блокирующий вызов. Весь сервер стоит, пока функция спит.
@app.get("/sleep/bad")
async def sleep_bad():
    time.sleep(1)
    return "bad: поспал 1 c и заблокировал всех"
