__all__ = ["RoomState", "ClientState"]


from collections import deque
from dataclasses import dataclass
import asyncio

from .messages import (
    UpdateUserMessage,
    ChallstrMessage,
    InitMessage,
    TitleMessage,
    UsersMessage,
    DeinitMessage,
)
from .utils import AsyncAttribute


class RoomState:
    def __init__(self, *, maxlogs=None):
        self.maxlogs = maxlogs
        self.logs = deque(maxlen=maxlogs)

        self.roomtype = AsyncAttribute()
        self.title = AsyncAttribute()
        self.userlist = AsyncAttribute()
        self.left = AsyncAttribute()

    async def handle_message(self, message):
        self.logs.append(message)

        if isinstance(message, InitMessage):
            self.roomtype.set(message.roomtype)

        elif isinstance(message, TitleMessage):
            self.title.set(message.title)

        elif isinstance(message, UsersMessage):
            self.userlist.set(message.userlist)

        elif isinstance(message, DeinitMessage):
            self.left.set(True)

    @property
    async def joined(self):
        await asyncio.gather(self.roomtype, self.title, self.userlist)
        return True


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
