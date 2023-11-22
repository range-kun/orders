from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: str


class CategoryOut(CategoryBase):
    id: int


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: str
    price: Decimal

    @field_validator("price")
    @classmethod
    def should_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Should be positive value")
        return v


class ProductCreate(ProductBase):
    category_id: int


class ProductCreated(ProductCreate):
    created: datetime
    id: int


class ProductOut(ProductBase):
    created: datetime
    category: CategoryOut | None = None
    id: int


class ProductPayload(BaseModel):
    id: int | None = None
    name: str | None = Field(None, min_length=1)
    description: str | None = None
    price: Decimal | None = None
    category: CategoryBase | None = None
    created: datetime | None = None


class EventType(Enum):
    delete = "delete"
    update = "update"
    add = "add"


class ProductEvent(BaseModel):
    event_type: EventType
    payload: ProductPayload
