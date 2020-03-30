# pslib

[![Build Status](https://travis-ci.com/vberlier/pslib.svg?branch=master)](https://travis-ci.com/vberlier/pslib)
[![PyPI](https://img.shields.io/pypi/v/pslib.svg)](https://pypi.org/project/pslib/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pslib.svg)](https://pypi.org/project/pslib/)

> A python library for interacting with Pokémon Showdown.

**🚧 Work in progress 🚧**

```python
import asyncio
import pslib

async def main():
    async with pslib.connect() as client:
        await client.login("username", "password")

        async for message in client.listen(pslib.PrivateMessage):
            print(message.sender, message.content)

asyncio.run(main())
```

## Installation

The package can be installed with `pip`.

```bash
$ pip install pslib
```

---

License - [MIT](https://github.com/vberlier/pslib/blob/master/LICENSE)
