from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.project import ProjectSimple

class TagRead(BaseModel):
    id: int
    slug: str
    name: str
    projects: list[ProjectSimple] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class TagListItem(BaseModel):
    id: int
    slug: str
    name: str
    count: int

class TagListResponse(BaseModel):
    items: list[TagListItem]
    limit: int
    offset: int