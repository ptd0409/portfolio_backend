from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class TagSimple(BaseModel):
    id: int
    slug: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class ProjectSimple(BaseModel):
    id: int
    slug: str
    title: str

    model_config = ConfigDict(from_attributes=True)

class ProjectListItem(BaseModel):
    id: int
    slug: str
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    published_at: Optional[datetime] = None

    tags: list[TagSimple] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class ProjectRead(BaseModel):
    id: int
    slug: str
    title: Optional[str] = None

    description: Optional[str] = None
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    repo_url: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    tags: list[TagSimple] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class ProjectCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=200)
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    repo_url: Optional[str] = None
    published_at: Optional[datetime] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    repo_url: Optional[str] = None
    published_at: Optional[datetime] = None
    tags: Optional[list[str]] = None

    model_config = ConfigDict(extra="forbid")