import sqlalchemy as sa
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils.functions.database import _set_url_database, make_url
from sqlalchemy_utils.functions.orm import quote


async def _get_scalar_result(engine, sql):
    try:
        async with engine.connect() as conn:
            return await conn.scalar(sql)
    except Exception as e:
        return False


async def database_exists(url):
    url = make_url(url)
    database = url.database
    engine = None
    try:
        text = "SELECT 1 FROM pg_database WHERE datname='%s'" % database
        for db in (database, "postgres", "template1", "template0", None):
            url = _set_url_database(url, database=db)
            engine = create_async_engine(url)
            try:
                return bool(
                    await _get_scalar_result(engine, sa.text(text)))
            except (ProgrammingError, OperationalError):
                pass
            return False
    finally:
        if engine:
            await engine.dispose()


async def create_database(url, encoding="utf8", template=None):
    url = make_url(url)
    database = url.database
    dialect_driver = url.get_dialect().driver

    url = _set_url_database(url, database="postgres")

    if dialect_driver in {"asyncpg", "pg8000", "psycopg2", "psycopg2cffi"}:
        engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    else:
        engine = create_async_engine(url)

    if not template:
        template = "template1"

    async with engine.begin() as conn:
        text = "CREATE DATABASE {} ENCODING '{}' TEMPLATE {}".format(
            quote(conn, database), encoding, quote(conn, template)
        )
        await conn.execute(sa.text(text))
    await engine.dispose()
