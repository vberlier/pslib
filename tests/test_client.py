import pytest
import asyncio

from pslib import (
    connect,
    ServerConnectionFailed,
    AlreadyJoinedRoom,
    AlreadyLeftRoom,
    UpdateUserMessage,
)


pytestmark = pytest.mark.asyncio


@pytest.mark.skip
@pytest.mark.timeout(30)
async def test_connect():
    async def log(name, client):
        async for message in client.listen(all_rooms=True):
            print(name, message.serialize())

    async def main(c1, c2):
        await asyncio.gather(c1.login("pslib-dev-ci-1"), c2.login("pslib-dev-ci-2"))
        print("SENDING")
        await c1.private_message("pslib-dev-ci-2", "hello")
        print("SUCCESS")
        await asyncio.sleep(3)

    async with connect() as c1, connect() as c2:
        await asyncio.gather(log("c1", c1), log("c2", c2), main(c1, c2))

    pytest.fail()


async def test_connect_host():
    async with connect(host="sim.smogon.com:8000") as client:
        async for message in client.listen(UpdateUserMessage):
            assert message.userid.startswith("guest")
            break


async def test_connect_uri():
    uri = "ws://sim.smogon.com:8000/showdown/123/abcdefgh/websocket"
    async with connect(uri=uri) as client:
        async for message in client.listen(UpdateUserMessage):
            assert message.userid.startswith("guest")
            break


async def test_connect_nonsticky_uri():
    with pytest.raises(ServerConnectionFailed):
        async with connect(uri="ws://sim.smogon.com:8000/showdown/websocket"):
            pass


async def test_connect_nonsticky_uri_correct():
    uri = "ws://sim.smogon.com:8000/showdown/websocket"
    async with connect(uri=uri, sticky=False) as client:
        async for message in client.listen(UpdateUserMessage):
            assert message.userid.startswith("guest")
            break


async def test_double_join(client):
    with pytest.raises(AlreadyJoinedRoom):
        await client.join("lobby")
        await client.join("lobby")


async def test_double_leave(client):
    with pytest.raises(AlreadyLeftRoom):
        await client.join("lobby")
        await client.leave("lobby")
        await client.leave("lobby")
