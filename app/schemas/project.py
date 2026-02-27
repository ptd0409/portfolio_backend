from __future__ import annotations

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.tag import TagRead

class ProjectRead(BaseModel):
    id: int
    slug: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    repo_url: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: list[TagRead] = []

    model_config = ConfigDict(from_attributes=True)