import uvicorn

from core.config.order_settings import get_settings
from src.orders.base_app import create_app
from src.orders.routes import category_router, product_router

settings = get_settings()
app = create_app(settings)

app.include_router(product_router)
app.include_router(category_router)


if __name__ == "__main__":
    uvicorn.run("src.orders:app", use_colors=True, reload=True)
