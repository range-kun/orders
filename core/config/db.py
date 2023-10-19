from pydantic_settings import BaseSettings


class ConfigDataBase(BaseSettings):
    DB_URL: str
    DB_ECHO_LOG: bool = False


settings_db = ConfigDataBase()
