from fastapi import FastAPI

from core.config.order_settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(**settings.model_dump())

    @app.on_event("startup")
    async def startup_evnet():
        pass

    @app.on_event("shutdown")
    async def shutdown_event():
        pass

    return app
