import asyncio
from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.postgres import PostgresContainer

from core.config.auth_settings import AuthSettings
from core.config.kafka_settings import KafkaSettings
from core.config.order_settings import Settings
from src.app import create_app
from src.auth.mixins import FetchMixin
from src.auth.schemas import AuthenticatedUser, AuthModel, TokenPair
from src.orders.tables import categories, meta, products
from tests.fixtures import auth_user, test_categories, test_products
from tests.utils import create_access_token, create_refresh_token

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def postgres_url() -> Generator[PostgresDsn, None, None]:
    with PostgresContainer("postgres:15.2") as container:
        connection_url = container.get_connection_url()
        postgres_dsn = connection_url.replace("+psycopg2", "+asyncpg")
        yield postgres_dsn


@pytest.fixture(scope="session")
def engine(postgres_url: str) -> AsyncEngine:
    return create_async_engine(postgres_url)


@pytest.fixture
def settings(postgres_url) -> Settings:
    settings = Settings(ASYNC_DB_URL=postgres_url)
    return settings


@pytest.fixture
def kafka_settings() -> KafkaSettings:
    settings = KafkaSettings()
    return settings


@pytest.fixture
def auth_settings() -> AuthSettings:
    settings = AuthSettings(
        JWT_SECRET_KEY="gee/tKlOi98R36YSE2XqKVqZqDJm60Ii7dhGn7Ct",
        JWT_REFRESH_SECRET_KEY="8kYimvOC7ZURin3sB8g/oNUU4CCSMLY+KPn2srka",
    )
    return settings


@pytest.fixture(scope="function", autouse=True)
async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)

    yield
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)


@pytest.fixture
def app(settings: Settings, kafka_settings: KafkaSettings, auth_settings: AuthSettings) -> FastAPI:
    return create_app(settings, kafka_settings, auth_settings)


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app, base_url="http://127.0.0.1:8080") as client:
        yield client


@pytest.fixture
def test_data_for_categories() -> list[dict]:
    return test_categories


@pytest.fixture
def test_data_for_products() -> list[dict]:
    return test_products


@pytest.fixture
def test_user() -> AuthenticatedUser:
    return AuthenticatedUser(**auth_user)


@pytest.fixture
def create_user_data() -> AuthModel:
    return AuthModel(username="username", password="password")


@pytest.fixture(scope="session", autouse=True)
async def mock_kafka_producer():
    with patch("src.orders.dependencies.AIOKafkaProducer", autospec=True) as mock_producer:
        mock_instance = mock_producer.return_value
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        yield mock_instance


@pytest.fixture
async def load_categories(engine, test_data_for_categories):
    async with engine.connect() as connection:
        stmt_categories = categories.insert().values(test_data_for_categories)
        await connection.execute(stmt_categories)
        await connection.commit()


@pytest.fixture
async def load_fixtures(engine, test_data_for_categories, test_data_for_products):
    async with engine.connect() as connection:
        stmt_categories = categories.insert().values(test_data_for_categories)
        stmt_products = products.insert().values(test_data_for_products)
        await connection.execute(stmt_categories)
        await connection.execute(stmt_products)
        await connection.commit()


@pytest.fixture
def token_pair(auth_settings: AuthSettings, test_user: AuthenticatedUser) -> TokenPair:
    access_token = create_access_token(auth_settings, test_user)
    refresh_token = create_refresh_token(auth_settings, test_user)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@pytest.fixture
def expired_token_pair(auth_settings: AuthSettings, test_user: AuthenticatedUser) -> TokenPair:
    access_token = create_access_token(auth_settings, test_user, exp_time=-60)
    refresh_token = create_refresh_token(auth_settings, test_user, exp_time=-60)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@pytest.fixture
async def authenticate_user(client: TestClient, token_pair):
    client.cookies = token_pair.model_dump()


@pytest.fixture
async def expired_authenticate_user(client: TestClient, expired_token_pair):
    client.cookies = expired_token_pair.model_dump()


@pytest.fixture
async def wrong_authentication(client: TestClient):
    client.cookies = {"access_token": "abcdefg", "refresh_token": "qwerty"}


@pytest.fixture
def mock_fetch_service(app, token_pair):
    with patch.object(FetchMixin, "fetch_token_pair") as mock_token_pair:
        mock_token_pair.return_value = token_pair
        yield


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
