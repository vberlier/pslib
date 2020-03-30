__all__ = ["RoomState", "ClientState"]


from collections import deque
from dataclasses import dataclass
import asyncio

from .messages import UpdateUserMessage, ChallstrMessage
from .utils import AsyncAttribute


class RoomState:
    def __init__(self, *, maxlogs=None):
        self.logs = deque(maxlen=maxlogs)

    async def handle_message(self, message):
        self.logs.append(message)


class ClientState(RoomState):
    @dataclass
    class UserInfo:
        userid: str
        named: bool
        avatar: int
        settings: dict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = AsyncAttribute()
        self.challstr = AsyncAttribute()

    async def handle_message(self, message):
        await super().handle_message(message)

        if isinstance(message, UpdateUserMessage):
            self.user.set(
                ClientState.UserInfo(
                    message.userid, message.named, message.avatar, message.settings,
                )
            )

        elif isinstance(message, ChallstrMessage):
            self.challstr.set(message.challstr)
