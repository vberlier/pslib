__all__ = ["HttpContext", "WebsocketContext"]


import json
import random
from string import ascii_lowercase, digits
from contextlib import asynccontextmanager

import aiohttp
import websockets

from .errors import ServerConnectionFailed, InvalidPayloadFormat


SERVER_INFO_URL = "https://pokemonshowdown.com/servers/{}.json"


class HttpContext:
    def __init__(self, session):
        self.session = session

    @classmethod
    @asynccontextmanager
    async def create(cls):
        async with aiohttp.ClientSession() as session:
            yield cls(session)

    async def get_json(self, *args, **kwargs):
        async with self.session.get(*args, **kwargs) as response:
            return await response.json()

    async def resolve_server_uri(self, server_id="showdown", *, server_host=None):
        if server_host is None:
            info = await self.get_json(SERVER_INFO_URL.format(server_id))
            server_host = "{host}:{port}".format(**info)

        server_number = "".join(random.choices(digits, k=3))
        session_id = "".join(random.choices(ascii_lowercase + digits, k=8))

        return f"ws://{server_host}/showdown/{server_number}/{session_id}/websocket"


class WebsocketContext:
    def __init__(self, protocol):
        self.protocol = protocol

    @classmethod
    @asynccontextmanager
    async def create(cls, uri, *, sticky=True):
        async with websockets.connect(uri) as ws:
            if sticky and await ws.recv() != "o":
                raise ServerConnectionFailed("Expected server acknowledgment")
            yield cls(ws)

    @staticmethod
    def decode_payload(payload):
        if not payload.startswith("a"):
            raise InvalidPayloadFormat("Expected prefix 'a'")

        try:
            data = json.loads(payload[1:])
        except json.JSONDecodeError as exc:
            raise InvalidPayloadFormat("Expected valid json") from exc

        for message_batch in data:
            room_id = "lobby"

            if message_batch.startswith(">"):
                room_id, _, message_batch = message_batch[1:].partition("\n")

            for line in message_batch.splitlines():
                if raw_message := line.strip():
                    yield room_id, raw_message

    async def raw_messages(self):
        async for payload in self.protocol:
            for room_id, raw_message in self.decode_payload(payload):
                yield room_id, raw_message
