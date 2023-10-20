from fastapi import FastAPI

from core.config.order_settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(**settings.model_dump())

    return app
