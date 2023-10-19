from pydantic_settings import BaseSettings


class ConfigDataBase(BaseSettings):
    ASYNC_DB_URL: str
    SYNC_DB_URL: str
    DB_ECHO_LOG: bool = False


settings_db = ConfigDataBase()
