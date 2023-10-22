from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    title: str = "Orders"
    debug: bool = False
    version: str = "0.1"
    ASYNC_DB_URL: str
    SYNC_DB_URL: str
    DB_ECHO_LOG: bool = False
