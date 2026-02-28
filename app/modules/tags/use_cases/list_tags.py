from __future__ import annotations

from app.modules.tags.ports import TagsRepoPort, TagWithCount

async def list_tags_uc(
    repo: TagsRepoPort,
    *,
    q: str | None,
    limit: int,
    offset: int
) -> list[TagWithCount]:
    return await repo.list_tags(q=q, limit=limit, offset=offset)