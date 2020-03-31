__all__ = ["InboundMessageManager", "OutboundMessageManager"]


from contextlib import asynccontextmanager
from weakref import WeakKeyDictionary
import asyncio

from .errors import ServerResponseTimeout
from .utils import race_against


class InboundMessageManager:
    def __init__(self):
        self.listeners = WeakKeyDictionary()

    def dispatch(self, message):
        for queue, message_types in self.listeners.items():
            if not message_types or isinstance(message, message_types):
                queue.put_nowait(message)

    async def listen(self, *message_types):
        queue = asyncio.Queue()
        self.listeners[queue] = message_types

        while message := await queue.get():
            yield message


class OutboundMessageManager:
    def __init__(self, *, messages_per_second=20, response_timeout=5):
        self.queue = asyncio.Queue()
        self.delay = 1 / messages_per_second
        self.response_timeout = response_timeout

    async def collect(self):
        while entry := await self.queue.get():
            raw_message, waiting = entry

            done = asyncio.Future()
            waiting.set_result(done)

            await asyncio.sleep(self.delay)

            try:
                yield raw_message
            finally:
                await done

    async def _raise_timeout_error(self):
        await asyncio.sleep(self.response_timeout)
        raise ServerResponseTimeout("Server took too long to respond")

    @asynccontextmanager
    async def append(self, raw_message):
        waiting = asyncio.Future()
        self.queue.put_nowait((raw_message, waiting))
        done = await waiting

        try:
            async with race_against(self._raise_timeout_error()):
                yield
        finally:
            done.set_result(None)
