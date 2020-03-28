import pytest

from pslib import __version__


pytestmark = pytest.mark.asyncio


async def test_version():
    assert __version__ == "0.0.0"
