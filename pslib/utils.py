__all__ = ["compose", "concurrent_tasks", "into_id", "AsyncAttribute", "race_against"]


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


class AsyncAttribute:
    def __init__(self):
        self.future = asyncio.Future()

    def __await__(self):
        return self.future.__await__()

    def set(self, value):
        if self.future.done():
            self.future = asyncio.Future()

        self.future.set_result(value)


@asynccontextmanager
async def race_against(coroutine):
    task = asyncio.current_task()
    coroutine_task = asyncio.create_task(coroutine)

    async def race():
        try:
            await coroutine_task
        except:
            pass

        task.cancel()

    try:
        async with concurrent_tasks(race()):
            yield
    except asyncio.CancelledError:
        if not coroutine_task.done():
            raise

        if exc := coroutine_task.exception():
            raise exc from None
