__all__ = ["HttpContext", "WebsocketContext"]


import json
import random
from string import ascii_lowercase, digits
from contextlib import asynccontextmanager

import aiohttp
import websockets

from .errors import (
    ServerConnectionFailed,
    InvalidPayloadFormat,
    ServerIdNotSpecified,
    InvalidServerActionResponse,
)


SERVER_INFO_URL = "https://pokemonshowdown.com/servers/{}.json"
SERVER_ACTION_URL = "https://play.pokemonshowdown.com/~~{}/action.php"


class HttpContext:
    def __init__(self, session):
        self.session = session
        self.server_id = None

    @classmethod
    @asynccontextmanager
    async def create(cls):
        async with aiohttp.ClientSession() as session:
            yield cls(session)

    async def get_info(self, *, server_id=None):
        server_id = server_id or self.server_id
        if not server_id:
            raise ServerIdNotSpecified("Expected explicit server_id")

        info_url = SERVER_INFO_URL.format(server_id)

        async with self.session.get(info_url) as response:
            return await response.json()

    async def post_action(self, data, *, server_id=None):
        server_id = server_id or self.server_id
        if not server_id:
            raise ServerIdNotSpecified("Expected explicit server_id")

        action_url = SERVER_ACTION_URL.format(server_id)

        async with self.session.post(action_url, data=data) as response:
            text = await response.text()

            if text.startswith("]"):
                try:
                    return json.loads(text[1:])
                except json.JSONDecodeError as exc:
                    raise InvalidServerActionResponse("Expected valid json") from exc
            else:
                return text

    async def resolve_server_uri(
        self, server_id="showdown", *, server_host=None, sticky=True
    ):
        if server_host is None:
            self.server_id = server_id
            info = await self.get_info()
            server_host = "{host}:{port}".format(**info)

        if not sticky:
            return f"ws://{server_host}/showdown/websocket"

        server_number = "".join(random.choices(digits, k=3))
        session_id = "".join(random.choices(ascii_lowercase + digits, k=8))

        return f"ws://{server_host}/showdown/{server_number}/{session_id}/websocket"


class WebsocketContext:
    def __init__(self, protocol, *, sticky=True):
        self.protocol = protocol
        self.sticky = sticky

    @classmethod
    @asynccontextmanager
    async def create(cls, uri, *, sticky=True):
        async with websockets.connect(uri) as ws:
            if sticky and await ws.recv() != "o":
                raise ServerConnectionFailed("Expected server acknowledgment")
            yield cls(ws, sticky=sticky)

    def decode_payload(self, payload):
        if self.sticky:
            if not payload.startswith("a"):
                raise InvalidPayloadFormat("Expected prefix 'a'")
            try:
                payload = json.loads(payload[1:])[0]
            except (json.JSONDecodeError, IndexError) as exc:
                raise InvalidPayloadFormat("Expected valid json") from exc

        room_id = "lobby"

        if payload.startswith(">"):
            room_id, _, payload = payload[1:].partition("\n")

        for line in payload.splitlines():
            if raw_message := line.strip():
                yield room_id, raw_message

    async def receive_raw_messages(self):
        async for payload in self.protocol:
            for room_id, raw_message in self.decode_payload(payload):
                yield room_id, raw_message

    async def send_raw_message(self, raw_message):
        data = json.dumps([raw_message]) if self.sticky else raw_message
        await self.protocol.send(data)
