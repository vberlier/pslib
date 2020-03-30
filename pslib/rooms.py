__all__ = ["RoomRegistry", "Room"]


from collections import deque
from contextlib import asynccontextmanager

from .commands import GlobalCommandsMixin


class RoomRegistry(dict):
    def __init__(self, client, *, maxlogs=None):
        self.client = client
        self.maxlogs = maxlogs

    def __missing__(self, room_id):
        room = Room(self.client, room_id, maxlogs=self.maxlogs)
        self[room_id] = room
        return room


class Room(GlobalCommandsMixin):
    def __init__(self, client, room_id, *, maxlogs=None):
        self.client = client
        self.id = room_id
        self.logs = deque(maxlen=maxlogs)

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id

    def _handle_message(self, message):
        self.logs.append(message)

    def serialize_logs(self):
        return "\n".join(message.serialize() or "|" for message in self.logs)

    async def listen(self, message_cls=None, *, all_rooms=False):
        async for message in self.client.received_messages.listen(message_cls):
            if all_rooms or message.room == self:
                yield message

    @asynccontextmanager
    async def send_message(self, message_text):
        async with self.client.sent_messages.append(f"{self.id}|{message_text}"):
            yield

    @asynccontextmanager
    async def send_command(self, command_name, *command_params):
        text = f"/{command_name}"

        if command_params:
            text += " " + ",".join(map(str, command_params))

        async with self.send_message(text):
            yield
