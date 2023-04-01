from sys import modules

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

from core.config import app_settings


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


Base = declarative_base()
if "pytest" in modules:
    base_dsn = app_settings.database_test_dsn
else:
    base_dsn = app_settings.database_dsn


engine = create_async_engine(base_dsn, echo=True, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
