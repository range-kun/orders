from typing import TypeVar

from pydantic import BaseModel

PyModel = TypeVar("PyModel", bound=BaseModel)
T = TypeVar("T", bound=BaseModel)
