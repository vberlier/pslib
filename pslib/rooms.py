__all__ = ["RoomRegistry", "Room"]


from contextlib import asynccontextmanager
from weakref import WeakValueDictionary

from .commands import GlobalCommandsMixin
from .errors import ReceivedErrorMessage
from .messages import ErrorMessage
from .state import RoomState
from .utils import race_against


class RoomRegistry(dict):
    def __init__(self, client, *, maxlogs=None):
        self.client = client
        self.maxlogs = maxlogs
        self.temporary_rooms = WeakValueDictionary()

    def __setitem__(self, room_id, room):
        super().__setitem__(room_id, room)
        if room_id in self.temporary_rooms:
            del self.temporary_rooms[room_id]

    def __missing__(self, room_id):
        if room := self.temporary_rooms.get(room_id):
            return room

        room = Room(self.client, room_id, RoomState(maxlogs=self.maxlogs))
        self.temporary_rooms[room_id] = room
        return room


class Room(GlobalCommandsMixin):
    def __init__(self, client, room_id, state):
        self.client = client
        self.id = room_id
        self.state = state

        self.joined = False

    async def handle_message(self, message):
        await self.state.handle_message(message)

    def handle_join(self):
        self.joined = True

        self.client.rooms[self.id] = self

    def handle_leave(self):
        self.joined = False
        self.reset_state()

        if self.id in self.client.rooms:
            del self.client.rooms[self.id]

    def reset_state(self):
        if self.id:
            self.state = type(self.state)(maxlogs=self.state.maxlogs)

    @property
    def logs(self):
        return "\n".join(message.serialize() or "|" for message in self.state.logs)

    async def listen(self, *message_types, all_rooms=False):
        async for message in self.client.received_messages.listen(*message_types):
            if all_rooms or message.room.id == self.id:
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
    async def check_message(self, message_text):
        async with self.client.sent_messages.append(f"{self.id}|{message_text}"):
            async with race_against(self._raise_error_message()):
                yield

    @asynccontextmanager
    async def check_command(self, command_name, *command_params):
        text = f"/{command_name}"

        if command_params:
            text += " " + ",".join(map(str, command_params))

        async with self.check_message(text):
            yield
