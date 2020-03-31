__all__ = [
    "parse_message",
    "Message",
    "UnrecognizedMessage",
    "PlainTextMessage",
    "ErrorMessage",
    "UpdateUserMessage",
    "ChallstrMessage",
    "PrivateMessage",
    "QueryResponseMessage",
    "InitMessage",
    "NoInitMessage",
    "TitleMessage",
    "UsersMessage",
    "DeinitMessage",
    "ChatMessage",
    "TimestampChatMessage",
    "TimestampMessage",
    "JoinMessage",
    "LeaveMessage",
    "NameMessage",
    "BattleMessage",
    "WinMessage",
    "RawMessage",
]


import json
from dataclasses import dataclass

from .errors import InvalidMessageParameters
from .utils import compose, into_id


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


class ErrorMessage(Message, match=["error"]):
    def hydrate(self):
        self.error = self.unpack(str)


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


class NoInitMessage(Message, match=["noinit"]):
    def hydrate(self):
        self.error, self.details = self.unpack(str, str)


class TitleMessage(Message, match=["title"]):
    def hydrate(self):
        self.title = self.unpack(str)


class UsersMessage(Message, match=["users"]):
    def hydrate(self):
        self.userlist = list(map(into_id, self.unpack(str).split(",")))


class DeinitMessage(Message, match=["deinit"]):
    pass


class ChatMessage(Message, match=["chat", "c"]):
    def hydrate(self):
        self.sender, self.content = self.unpack(into_id, str)


class TimestampChatMessage(ChatMessage, match=["c:"]):
    def hydrate(self):
        self.timestamp, self.sender, self.content = self.unpack(int, into_id, str)


class TimestampMessage(Message, match=[":"]):
    def hydrate(self):
        self.timestamp = self.unpack(int)


class JoinMessage(Message, match=["join", "j", "J"]):
    def hydrate(self):
        self.joined = self.unpack(into_id)


class LeaveMessage(Message, match=["leave", "l", "L"]):
    def hydrate(self):
        self.left = self.unpack(into_id)


class NameMessage(Message, match=["name", "n", "N"]):
    def hydrate(self):
        self.new_userid, self.old_userid = self.unpack(into_id, into_id)


class BattleMessage(Message, match=["battle", "b", "B"]):
    def hydrate(self):
        battle_id, self.p1, self.p2 = self.unpack(str, into_id, into_id)
        self.battle = self.room.client.rooms[battle_id]


class WinMessage(Message, match=["win"]):
    def hydrate(self):
        self.userid = self.unpack(into_id)


class RawMessage(Message, match=["raw"]):
    pass
