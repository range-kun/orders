from datetime import datetime

import sqlalchemy as sa

from core.db import meta

products = sa.Table(
    "products",
    meta,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(length=50), nullable=False),
    sa.Column("description", sa.Text),
    sa.Column("price", sa.DECIMAL(12, 2), nullable=False),
    sa.Column("created", sa.DateTime, default=datetime.utcnow()),
    sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id"), nullable=False),
)


categories = sa.Table(
    "categories",
    meta,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(length=50), nullable=False),
    sa.Column("description", sa.Text),
)

__all__ = [products, categories]
