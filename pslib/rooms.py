__all__ = ["RoomRegistry", "Room"]


from contextlib import asynccontextmanager

from .commands import GlobalCommandsMixin
from .errors import ReceivedErrorMessage
from .messages import ErrorMessage
from .state import RoomState
from .utils import race_against


class RoomRegistry(dict):
    def __init__(self, client, *, maxlogs=None):
        self.client = client
        self.maxlogs = maxlogs

    def __missing__(self, room_id):
        room = Room(self.client, room_id, RoomState(maxlogs=self.maxlogs))
        self[room_id] = room
        return room


class Room(GlobalCommandsMixin):
    def __init__(self, client, room_id, state):
        self.client = client
        self.id = room_id
        self.state = state

    async def handle_message(self, message):
        await self.state.handle_message(message)

    def reset_state(self):
        self.state = type(self.state)(maxlogs=self.state.maxlogs)

    @property
    def logs(self):
        return "\n".join(message.serialize() or "|" for message in self.state.logs)

    async def listen(self, *message_types, all_rooms=False):
        async for message in self.client.received_messages.listen(*message_types):
            if all_rooms or message.room is self:
                yield message

    async def expect(self, *message_types, all_rooms=False, **attrs):
        async for message in self.listen(*message_types, all_rooms=all_rooms):
            if all(
                hasattr(message, key) and getattr(message, key) == value
                for key, value in attrs.items()
            ):
                return message

    async def _raise_error_message(self):
        message = await self.expect(ErrorMessage)
        raise ReceivedErrorMessage(message.error)

    @asynccontextmanager
    async def send_message(self, message_text):
        async with self.client.sent_messages.append(f"{self.id}|{message_text}"):
            async with race_against(self._raise_error_message()):
                yield

    @asynccontextmanager
    async def send_command(self, command_name, *command_params):
        text = f"/{command_name}"

        if command_params:
            text += " " + ",".join(map(str, command_params))

        async with self.send_message(text):
            yield
