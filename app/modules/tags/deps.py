from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.modules.tags.adapters.repo_sqlalchemy import TagsRepoSQLAlchemy
from app.modules.tags.ports import TagsRepoPort

def get_tags_repo(db: AsyncSession = Depends(get_db)) -> TagsRepoPort:
    return TagsRepoSQLAlchemy(db)