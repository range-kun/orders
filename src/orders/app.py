from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core.config.order_settings import Settings
from src.orders.routes import category_router, product_router


def create_app(settings_: Settings) -> FastAPI:
    @asynccontextmanager
    async def lifespan(fast_api_app: FastAPI):
        fast_api_app.state.settings = settings_
        yield

    fast_api_app = FastAPI(lifespan=lifespan, **settings_.model_dump())

    fast_api_app.include_router(product_router)
    fast_api_app.include_router(category_router)

    return fast_api_app


if __name__ == "__main__":
    settings = Settings()
    app = create_app(settings)

    uvicorn.run(app, use_colors=True, port=8008, host="0.0.0.0")
