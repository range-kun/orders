from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core.config.kafka_settings import KafkaSettings
from core.config.order_settings import Settings
from src.orders.routes import category_router, product_router


def create_app(settings_: Settings, kafka_settings: KafkaSettings) -> FastAPI:
    @asynccontextmanager
    async def lifespan(fast_api_app: FastAPI):
        fast_api_app.state.settings = settings_
        fast_api_app.state.kafka_settings = kafka_settings
        yield

    fast_api_app = FastAPI(lifespan=lifespan, **settings_.model_dump())

    fast_api_app.include_router(product_router)
    fast_api_app.include_router(category_router)

    return fast_api_app


if __name__ == "__main__":
    settings = Settings()
    kafka_setting = KafkaSettings()
    app = create_app(settings, kafka_setting)

    uvicorn.run(app, use_colors=True, port=settings.APP_PORT, host=settings.APP_HOST)
