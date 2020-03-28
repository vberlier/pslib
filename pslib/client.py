__all__ = ["Client"]


from contextlib import asynccontextmanager
from dataclasses import dataclass

from .network import HttpContext, WebsocketContext


@dataclass
class Client:
    http: HttpContext
    ws: WebsocketContext

    @classmethod
    @asynccontextmanager
    async def connect(cls, server="showdown", *, host=None, uri=None):
        async with HttpContext.create() as http:
            if uri is None:
                uri = await http.resolve_server_uri(server=server, host=host)
            async with WebsocketContext.create(uri) as ws:
                yield cls(http, ws)
