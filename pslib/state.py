__all__ = ["RoomState"]


from collections import deque


class RoomState:
    def __init__(self, *, maxlogs=None):
        self.logs = deque(maxlen=maxlogs)

    async def handle_message(self, message):
        self.logs.append(message)
