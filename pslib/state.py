__all__ = ["RoomState", "ClientState"]


from collections import deque
from dataclasses import dataclass
import asyncio

from .messages import UpdateUserMessage, ChallstrMessage


class RoomState:
    def __init__(self, *, maxlogs=None):
        self.logs = deque(maxlen=maxlogs)

    async def handle_message(self, message):
        self.logs.append(message)


class ClientState(RoomState):
    @dataclass
    class UserInfo:
        username: str
        busy: bool
        named: bool
        avatar: int
        settings: dict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = asyncio.Future()
        self.challstr = asyncio.Future()

    async def handle_message(self, message):
        await super().handle_message(message)

        if isinstance(message, UpdateUserMessage):
            if self.user.done():
                self.user = asyncio.Future()

            self.user.set_result(
                ClientState.UserInfo(
                    message.username,
                    message.busy,
                    message.named,
                    message.avatar,
                    message.settings,
                )
            )

        elif isinstance(message, ChallstrMessage):
            if self.challstr.done():
                self.challstr = asyncio.Future()

            self.challstr.set_result(message.challstr)
