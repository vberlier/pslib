__all__ = [
    "parse_message",
    "InboundMessageManager",
    "OutboundMessageManager",
    "Message",
    "UnrecognizedMessage",
    "PlainTextMessage",
    "UpdateUserMessage",
    "QueryResponseMessage",
    "WinMessage",
    "RawMessage",
]


import json
import itertools
from contextlib import asynccontextmanager
from collections import defaultdict
from weakref import WeakSet
from dataclasses import dataclass
import asyncio

from .errors import InvalidMessageParameters
from .utils import compose


MESSAGE_CLASS_REGISTRY = {}


def parse_message(raw_message):
    message_type = ""
    if raw_message.startswith("|"):
        message_type, _, raw_message = raw_message[1:].partition("|")

    cls = MESSAGE_CLASS_REGISTRY.get(message_type, UnrecognizedMessage)
    return cls(message_type, raw_message)


class InboundMessageManager:
    def __init__(self):
        self.listeners = defaultdict(WeakSet)

    def dispatch(self, message):
        generic = self.listeners[None]
        specific = self.listeners[type(message)]

        for listener in itertools.chain(generic, specific):
            listener.put_nowait(message)

    async def listen(self, message_cls=None):
        queue = asyncio.Queue()
        self.listeners[message_cls].add(queue)

        while message := await queue.get():
            yield message


class OutboundMessageManager:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def collect(self):
        while entry := await self.queue.get():
            raw_message, waiting = entry

            try:
                yield raw_message
            finally:
                done = asyncio.Future()
                waiting.set_result(done)
                await done

    @asynccontextmanager
    async def append(self, raw_message):
        waiting = asyncio.Future()
        self.queue.put_nowait((raw_message, waiting))
        done = await waiting

        try:
            yield
        finally:
            done.set_result(None)


@dataclass
class Message:
    type: str
    value: str

    def __init_subclass__(cls, match=()):
        for message_type in match:
            MESSAGE_CLASS_REGISTRY[message_type] = cls

    def __post_init__(self):
        self.hydrate()

    def hydrate(self):
        pass

    def unpack(self, *transformers):
        params = self.value.split("|", len(transformers))

        if len(params) != len(transformers):
            raise InvalidMessageParameters(f"Expected {len(transformers)} parameters")

        return (func(param) for param, func in zip(params, transformers))

    def set_room(self, room):
        self.room = room
        room._handle_message(self)

    def serialize(self):
        return f"|{self.type}|{self.value}"


class UnrecognizedMessage(Message):
    pass


class PlainTextMessage(Message, match=[""]):
    def serialize(self):
        return self.value


class UpdateUserMessage(Message, match=["updateuser"]):
    def hydrate(self):
        self.user, self.named, self.avatar, self.settings = self.unpack(
            str, compose(bool, int), int, json.loads
        )


class QueryResponseMessage(Message, match=["queryresponse"]):
    def hydrate(self):
        self.querytype, self.result = self.unpack(str, json.loads)


class WinMessage(Message, match=["win"]):
    def hydrate(self):
        (self.user_id,) = self.unpack(str)


class RawMessage(Message, match=["raw"]):
    pass
