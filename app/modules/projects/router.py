from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.modules.projects.service import get_projects
from app.schemas.common import APIResponse, PaginationMeta
from app.schemas.project import ProjectRead

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=APIResponse[list[ProjectRead]])
async def list_projects_endpoint(
    q: Optional[str] = Query(default=None, description="Search by title or description"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    items, total = await get_projects(
        db,
        q=q,
        page=page,
        limit=limit
    )

    meta = PaginationMeta(
        page=page,
        limit=limit,
        total=total
    )

    return APIResponse(
        data=items,
        meta=meta,
        message="success"
    )