__all__ = ["compose", "concurrent_tasks", "into_id"]


import re
import asyncio
from contextlib import asynccontextmanager


def compose(*funcs):
    def wrapper(value):
        for func in reversed(funcs):
            value = func(value)
        return value

    return wrapper


@asynccontextmanager
async def concurrent_tasks(*coroutines):
    tasks = list(map(asyncio.create_task, coroutines))

    try:
        yield
    finally:
        for task in tasks:
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass


def into_id(string):
    return re.sub(r"(\W|_)", "", string.lower())
