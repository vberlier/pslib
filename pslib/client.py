__all__ = ["Client"]


from contextlib import asynccontextmanager

from .network import HttpContext, WebsocketContext
from .messages import InboundMessageManager, OutboundMessageManager, parse_message
from .rooms import RoomRegistry, Room
from .utils import concurrent_tasks


class Client(Room):
    def __init__(self, http, ws):
        super().__init__(self, "", maxlogs=100)

        self.http = http
        self.ws = ws

        self.rooms = RoomRegistry(self)
        self.rooms["lobby"] = self

        self.received_messages = InboundMessageManager()
        self.sent_messages = OutboundMessageManager()

    @classmethod
    @asynccontextmanager
    async def connect(cls, server="showdown", *, host=None, uri=None, sticky=True):
        async with HttpContext.create() as http:
            if uri is None:
                uri = await http.resolve_server_uri(server_id=server, server_host=host)
            async with WebsocketContext.create(uri, sticky=sticky) as ws:
                async with cls(http, ws).start() as client:
                    yield client

    @asynccontextmanager
    async def start(self):
        async with concurrent_tasks(self._receive_messages(), self._send_messages()):
            yield self

    async def _receive_messages(self):
        async for room_id, raw_message in self.ws.receive_raw_messages():
            message = parse_message(raw_message)
            message.set_room(self.rooms[room_id])
            self.received_messages.dispatch(message)

    async def _send_messages(self):
        async for raw_message in self.sent_messages.collect():
            await self.ws.send_raw_message(raw_message)
