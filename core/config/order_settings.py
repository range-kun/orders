import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    title: str = "Orders"
    debug: bool = False
    version: str = "0.1"
    ASYNC_DB_URL: str = f"sqlite+aiosqlite:///{os.path.join(os.getcwd(), 'database.db')}"
    SYNC_DB_URL: str = f"sqlite:///{os.path.join(os.getcwd(), 'database.db')}"
    DB_ECHO_LOG: bool = False
