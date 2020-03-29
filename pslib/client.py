__all__ = ["Client"]


from contextlib import asynccontextmanager
from dataclasses import dataclass

from .network import HttpContext, WebsocketContext
from .messages import parse_message


@dataclass
class Client:
    http: HttpContext
    ws: WebsocketContext

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
