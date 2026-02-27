from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from app.schemas.project import ProjectRead

class TagRead(BaseModel):
    id: int
    slug: str
    name: str
    project: list[ProjectRead] = []

    model_config = ConfigDict(from_attributes=True)