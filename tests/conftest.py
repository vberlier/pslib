import pytest

from pslib import connect


@pytest.fixture
async def client():
    uri = "ws://sim.smogon.com:8000/showdown/websocket"
    async with connect(uri=uri, sticky=False) as client:
        yield client
