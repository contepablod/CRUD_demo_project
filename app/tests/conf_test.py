import os

import pytest_asyncio

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")


@pytest_asyncio.fixture(scope="session")
async def anyio_backend():
    # let pytest-asyncio/anyio drive the event loop
    return "asyncio"
