import pytest

from pslib import Client


@pytest.fixture
async def client():
    async with Client.connect() as client:
        yield client
