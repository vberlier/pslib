__all__ = [
    "parse_message",
    "Message",
    "UnrecognizedMessage",
    "PlainTextMessage",
    "UpdateUserMessage",
]


import json
from dataclasses import dataclass

from .errors import InvalidMessageParameters
from .utils import compose


MESSAGE_CLASS_REGISTRY = {}


def parse_message(raw_message):
    message_type = ""
    if raw_message.startswith("|"):
        message_type, _, raw_message = raw_message[1:].partition("|")

    cls = MESSAGE_CLASS_REGISTRY.get(message_type, UnrecognizedMessage)
    return cls(message_type, raw_message)


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
