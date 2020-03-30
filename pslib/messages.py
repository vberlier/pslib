__all__ = [
    "parse_message",
    "InboundMessageManager",
    "OutboundMessageManager",
    "Message",
    "UnrecognizedMessage",
    "PlainTextMessage",
    "UpdateUserMessage",
    "ChallstrMessage",
    "PrivateMessage",
    "QueryResponseMessage",
    "InitMessage",
    "TitleMessage",
    "UsersMessage",
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
from .utils import compose, into_id


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
        params = self.value.split("|", len(transformers) - 1)

        if len(params) != len(transformers):
            raise InvalidMessageParameters(f"Expected {len(transformers)} parameters")

        unpacked = [func(param) for param, func in zip(params, transformers)]
        return unpacked[0] if len(transformers) == 1 else unpacked

    def serialize(self):
        return f"|{self.type}|{self.value}"


class UnrecognizedMessage(Message):
    pass


class PlainTextMessage(Message, match=[""]):
    def serialize(self):
        return self.value


class UpdateUserMessage(Message, match=["updateuser"]):
    def hydrate(self):
        self.userid, self.named, self.avatar, self.settings = self.unpack(
            into_id, compose(bool, int), int, json.loads
        )


class ChallstrMessage(Message, match=["challstr"]):
    def hydrate(self):
        self.challstr = self.unpack(str)


class PrivateMessage(Message, match=["pm"]):
    def hydrate(self):
        self.sender, self.receiver, self.content = self.unpack(into_id, into_id, str)


class QueryResponseMessage(Message, match=["queryresponse"]):
    def hydrate(self):
        self.querytype, self.result = self.unpack(str, json.loads)


class InitMessage(Message, match=["init"]):
    def hydrate(self):
        self.roomtype = self.unpack(str)


class TitleMessage(Message, match=["title"]):
    def hydrate(self):
        self.title = self.unpack(str)


class UsersMessage(Message, match=["users"]):
    def hydrate(self):
        self.userlist = list(map(into_id, self.unpack(str).split(",")))


class WinMessage(Message, match=["win"]):
    def hydrate(self):
        self.user_id = self.unpack(str)


class RawMessage(Message, match=["raw"]):
    pass
