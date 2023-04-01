import os

from pydantic import BaseSettings, PostgresDsn, parse_obj_as

dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")


class DBSettings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: str
    postgres_server: str = "postgres"
    postgres_port: str = "5432"
    postgres_db: str = "postgres"
    postgres_db_test: str = "postgres_test"

    class Config:
        env_file = dotenv_path


db_set = DBSettings()


class AppSettings(BaseSettings):
    project_name: str = "FileStorage"
    project_host: str = "127.0.0.1"
    project_port: int = 8080

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    database_dsn: PostgresDsn = parse_obj_as(
        PostgresDsn,
        f"postgresql+asyncpg://{db_set.postgres_user}:"
        f"{db_set.postgres_password}@{db_set.postgres_server}:"
        f"{db_set.postgres_port}/{db_set.postgres_db}",
    )
    database_test_dsn: PostgresDsn = parse_obj_as(
        PostgresDsn,
        f"postgresql+asyncpg://{db_set.postgres_user}:"
        f"{db_set.postgres_password}@{db_set.postgres_server}:"
        f"{db_set.postgres_port}/{db_set.postgres_db_test}",
    )

    class Config:
        env_file = dotenv_path


app_settings = AppSettings()
