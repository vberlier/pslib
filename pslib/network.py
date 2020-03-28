__all__ = ["HttpContext", "WebsocketContext"]


from random import choices
from string import ascii_lowercase, digits
from dataclasses import dataclass
from contextlib import asynccontextmanager

import aiohttp
import websockets

from .errors import ShowdownConnectionFailed


SERVER_INFO_URL = "https://pokemonshowdown.com/servers/{}.json"


@dataclass
class HttpContext:
    session: aiohttp.ClientSession

    @classmethod
    @asynccontextmanager
    async def create(cls):
        async with aiohttp.ClientSession() as session:
            yield cls(session)

    async def get_json(self, *args, **kwargs):
        async with self.session.get(*args, **kwargs) as response:
            return await response.json()

    async def resolve_server_uri(self, server="showdown", *, host=None):
        if host is None:
            info = await self.get_json(SERVER_INFO_URL.format(server))
            host = "{host}:{port}".format(**info)

        server_number = "".join(choices(digits, k=3))
        session_id = "".join(choices(ascii_lowercase + digits, k=8))

        return f"ws://{host}/showdown/{server_number}/{session_id}/websocket"


@dataclass
class WebsocketContext:
    protocol: websockets.WebSocketClientProtocol

    @classmethod
    @asynccontextmanager
    async def create(cls, uri):
        async with websockets.connect(uri) as ws:
            if await ws.recv() != "o":
                raise ShowdownConnectionFailed()
            yield cls(ws)
