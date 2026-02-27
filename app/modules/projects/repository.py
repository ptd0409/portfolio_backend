from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import Select, desc, func, or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

async def list_projects(
        db: AsyncSession,
        *,
        q: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
) -> tuple[list[Project], int]:
    """
    return:
        - items: list[Project]
        - total: total rows for pagination
    """
    stmt: Select = select(Project).options(selectinload(Project.tags))

    if q:
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Project.title.ilike(pattern),
                Project.slug.ilike(pattern), 
                Project.description.ilike(pattern)
            )
        )
    
    # order
    stmt = stmt.order_by(
        desc(Project.published_at).nullslast(),
        desc(Project.created_at).nullslast()
    )

    # total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    # pagination
    safe_page = max(page, 1)
    safe_limit = min(max(limit, 1), 100)
    offset = (safe_page -1) * safe_limit

    stmt = stmt.offset(offset).limit(safe_limit)

    rows: Sequence[Project] = (await db.execute(stmt)).scalars().all()
    return list(rows), int(total)

async def get_project_by_slug(
    db: AsyncSession,
    *,
    slug: str
) -> Optional[Project]:
    stmt = (
        select(Project).where(Project.slug == slug).options(selectinload(Project.tags))
    )
    return (await db.execute(stmt)).scalar_one_or_none()

async def create_project(
    db: AsyncSession,
    *,
    payload: ProjectCreate
) -> ProjectCreate:
    project = Project(
        slug=payload.slug.strip(),
        title=payload.title,
        description=payload.description,
        content=payload.content,
        cover_image_url=payload.cover_image_url,
        repo_url=payload.repo_url,
        published_at=payload.published_at
    )

    db.add(project)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(project)
    return project