"""Шлёт 10 одновременных запросов на каждый эндпоинт и меряет общее время."""
import asyncio
import time

import httpx


async def hit(path: str, n: int = 10) -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=60) as client:
        start = time.perf_counter()
        await asyncio.gather(*(client.get(path) for _ in range(n)))
        print(f"{path:<14} {n} запросов за {time.perf_counter() - start:.1f} c")


for path in ["/sleep/sync", "/sleep/async", "/sleep/bad"]:
    asyncio.run(hit(path))
