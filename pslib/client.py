__all__ = ["Client"]


from contextlib import asynccontextmanager

from .network import HttpContext, WebsocketContext
from .messages import parse_message


class Client:
    def __init__(self, http, ws):
        self.http = http
        self.ws = ws

    @classmethod
    @asynccontextmanager
    async def connect(cls, server="showdown", *, host=None, uri=None, sticky=True):
        async with HttpContext.create() as http:
            if uri is None:
                uri = await http.resolve_server_uri(server_id=server, server_host=host)
            async with WebsocketContext.create(uri, sticky=sticky) as ws:
                yield cls(http, ws)

    async def listen(self):
        async for room, raw_message in self.ws.raw_messages():
            yield parse_message(raw_message)
