import pytest

from pslib import Client


pytestmark = pytest.mark.asyncio


async def test_connect():
    async with Client.connect():
        pass


async def test_connect_server():
    async with Client.connect("smogtours"):
        pass


async def test_connect_host():
    async with Client.connect(host="sim.smogon.com:8000"):
        pass


async def test_connect_uri():
    uri = "ws://sim.smogon.com:8000/showdown/123/abcdefgh/websocket"
    async with Client.connect(uri=uri):
        pass
