from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    title: str = "Orders"
    debug: bool = False
    version: str = "0.1"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
