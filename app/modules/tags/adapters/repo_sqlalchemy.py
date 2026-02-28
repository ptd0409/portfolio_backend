from __future__ import annotations

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.models.project_tag import project_tag
from app.modules.tags.ports import TagWithCount, TagsRepoPort

class TagsRepoSQLAlchemy(TagsRepoPort):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_tags(self, q: str | None, limit: int, offset: int) -> list[TagWithCount]:
        stmt = (
            select(
                Tag.id,
                Tag.slug,
                Tag.name,
                func.count(project_tag.c.project_id).label("count")
            )
            .select_from(Tag)
            .outerjoin(project_tag, Tag.id == project_tag.c.tag_id)
            .group_by(Tag.id)
            .order_by(func.count(project_tag.c.project_id).desc(), Tag.name.asc())
            .limit(limit)
            .offset(offset)
        )
        
        if q:
            q2 = q.strip().lower()
            like = f"%{q2}%"
            stmt = stmt.where(
                or_(
                    func.lower(Tag.name).like(like),
                    func.lower(Tag.slug).like(like)
                )
            )

        res = await self.db.execute(stmt)
        rows = res.all()

        return [
            TagWithCount(
                id=r.id,
                slug=r.slug,
                name=r.name,
                count=int(r.count)
            )
            for r in rows
        ]
