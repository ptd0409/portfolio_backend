from __future__ import annotations

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class APIResponse(GenericModel, Generic[T]):
    data: T
    meta: Optional[PaginationMeta] = None
    message: str = "Success"

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int

class ErrorResponse(BaseModel):
    detail: str
    missing: Optional[list[str]] = None