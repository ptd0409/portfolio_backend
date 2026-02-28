from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.schemas.tag import TagListResponse, TagListItem
from app.modules.tags.deps import get_tags_repo
from app.modules.tags.ports import TagsRepoPort
from app.modules.tags.use_cases.list_tags import list_tags_uc

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("", response_model=TagListResponse)
async def get_tags(
    q: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    repo: TagsRepoPort = Depends(get_tags_repo)
):
    rows = await list_tags_uc(repo, q=q, limit=limit, offset=offset)
    items = [TagListItem(**r.__dict__) for r in rows]
    return TagListResponse(items=items, limit=limit, offset=offset)