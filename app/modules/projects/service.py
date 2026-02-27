from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects import repository
from app.models.project import Project

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
        status=status,
        page=page,
        limit=limit
    )