from collections import deque


__all__ = ["RoomRegistry", "Room"]


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

    def handle_message(self, message):
        self.logs.append(message)

    def serialize_logs(self):
        return "\n".join(message.serialize() or "|" for message in self.logs)
