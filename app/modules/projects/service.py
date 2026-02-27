from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException

from app.modules.projects import repository
from app.models.project import Project
from app.schemas.project import ProjectCreate

async def get_projects(
    db: AsyncSession,
    *,
    q: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> tuple[list[Project], int]:

    return await repository.list_projects(
        db,
        q=q,
        page=page,
        limit=limit
    )

async def get_project_detail(
    db: AsyncSession,
    *,
    slug: str
) -> Optional[Project]:
    return await repository.get_project_by_slug(db, slug=slug)

async def create_project(
    db: AsyncSession,
    *,
    payload: ProjectCreate
) -> Project:
    existing = await repository.get_project_by_slug(db, slug=payload.slug.strip())
    if existing:
        raise HTTPException(status_code=409, detail="Slug already exists")
    try:
        return await repository.create_project(db, payload=payload)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Slug already exists")