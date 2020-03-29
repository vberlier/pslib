__all__ = ["RoomRegistry", "Room"]


from collections import deque


class RoomRegistry(dict):
    def __init__(self, client, *, maxlogs=None):
        self.client = client
        self.maxlogs = maxlogs

    def __missing__(self, room_id):
        room = Room(self.client, room_id, maxlogs=self.maxlogs)
        self[room_id] = room
        return room


class Room:
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
