import asyncio
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.postgres import PostgresContainer

from core.config.kafka_settings import KafkaSettings
from core.config.order_settings import Settings
from src.orders.app import create_app
from src.orders.tables import categories, meta, products
from src.orders.tests.fixtures import test_categories, test_products

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


@pytest.fixture(scope="function", autouse=True)
async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)

    yield
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)


@pytest.fixture
def app(settings: Settings, kafka_settings: KafkaSettings) -> FastAPI:
    return create_app(settings, kafka_settings)


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


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
