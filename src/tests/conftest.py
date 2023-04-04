from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.sqlalhemy_utils_async import database_exists, create_database
from db.database import Base, engine
from main import app


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def async_session() -> AsyncSession:
    if not await database_exists(engine.url):
        await create_database(engine.url)
    session = async_sessionmaker(engine, expire_on_commit=False)
    async with session():
        async with engine.begin() as connect:
            await connect.run_sync(Base.metadata.create_all)

        yield session

    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
def prefix_file_url() -> str:
    return "/api/v1/files"


@pytest.fixture(scope="session")
def prefix_user_url() -> str:
    return "/api/v1/user"


@pytest.fixture(scope="session")
def user_test_data() -> dict:
    return {"name": "test_user", "password": "my_secret_password"}


@pytest.fixture(scope="session")
def test_file() -> Path:
    return Path("tests/test-file.txt")
