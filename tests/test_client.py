import pytest

from pslib import Client


pytestmark = pytest.mark.asyncio


async def test_connect():
    async with Client.connect():
        pass
