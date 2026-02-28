from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import Select, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.modules.projects.ports import ProjectRepoPort

from app.models.tag import Tag
from app.modules.projects.utils import normalize_tag_slugs

class SqlAlchemyProjectRepo(ProjectRepoPort):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def exists_by_slug(self, *, slug: str) -> bool:
        stmt = select(func.count()).select_from(Project).where(Project.slug == slug)
        count = (await self.db.execute(stmt)).scalar_one()
        return int(count) > 0
    
    async def list(
        self,
        *,
        q: Optional[str],
        page: int,
        limit: int,
        with_tags: bool = True
    ) -> tuple[list[Project], int]:
        stmt: Select = select(Project)

        if with_tags:
            stmt = stmt.options(selectinload(Project.tags))

        if q:
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Project.title.ilike(pattern),
                    Project.slug.ilike(pattern),
                    Project.description.ilike(pattern)
                )
            )
        
        stmt = stmt.order_by(
            desc(Project.published_at).nullslast(),
            desc(Project.created_at).nullslast()
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        safe_page = max(page, 1)
        safe_limit = min(max(limit, 1), 100)
        offset = (safe_page - 1) * safe_limit

        stmt = stmt.offset(offset).limit(safe_limit)

        rows: Sequence[Project] = (await self.db.execute(stmt)).scalars().all()
        return list(rows), int(total)

    async def get_by_slug(
        self,
        *,
        slug: str,
        with_tags: bool = True
    ) -> Optional[Project]:
        stmt = select(Project).where(Project.slug == slug)
        if with_tags:
            stmt = stmt.options(selectinload(Project.tags))
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def create(
        self,
        *,
        payload: ProjectCreate
    ) -> Project:
        project = Project(
            slug=payload.slug.strip(),
            title=payload.title,
            description=payload.description,
            content=payload.content,
            cover_image_url=payload.cover_image_url,
            repo_url=payload.repo_url,
            published_at=payload.published_at
        )
        self.db.add(project)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        #await self.db.refresh(project)
        #return project
        return await self.get_by_slug(slug=project.slug, with_tags=True)
    
    async def update_by_slug(
        self,
        *,
        slug: str,
        payload: ProjectUpdate,
    ) -> Optional[Project]:
        project = await self.get_by_slug(slug=slug, with_tags=True)
        if not project:
            return None

        patch = payload.model_dump(exclude_unset=True)
        if not patch:
            return project

        tags_input = patch.pop("tags", None)

        for k, v in patch.items():
            setattr(project, k, v)

        if tags_input is not None:
            slugs = normalize_tag_slugs(tags_input)

            if not slugs:
                project.tags = []
            else:
                stmt = select(Tag).where(Tag.slug.in_(slugs))
                existing = (await self.db.execute(stmt)).scalars().all()
                by_slug = {t.slug: t for t in existing}

                created: list[Tag] = []
                for s in slugs:
                    if s in by_slug:
                        continue
                    t = Tag(slug=s, name=s)
                    self.db.add(t)
                    created.append(t)

                if created:
                    await self.db.flush()

                by_slug.update({t.slug: t for t in created})
                project.tags = [by_slug[s] for s in slugs if s in by_slug]

        self.db.add(project)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise

        await self.db.refresh(project)
        return await self.get_by_slug(slug=slug, with_tags=True)