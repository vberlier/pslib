import pytest

from pslib import Client, ServerConnectionFailed


pytestmark = pytest.mark.skip  # Temporarily skip client tests


async def test_connect():
    async with Client.connect():
        pass


async def test_connect_host():
    async with Client.connect(host="sim.smogon.com:8000"):
        pass


async def test_connect_uri():
    uri = "ws://sim.smogon.com:8000/showdown/123/abcdefgh/websocket"
    async with Client.connect(uri=uri):
        pass


async def test_connect_nonsticky_uri():
    with pytest.raises(ServerConnectionFailed):
        async with Client.connect(uri="ws://sim.smogon.com:8000/showdown/websocket"):
            pass


async def test_connect_nonsticky_uri_correct():
    uri = "ws://sim.smogon.com:8000/showdown/websocket"
    async with Client.connect(uri=uri, sticky=False):
        pass
