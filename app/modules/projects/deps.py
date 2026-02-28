from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.modules.projects.adapters.repo_sqlalchemy import SqlAlchemyProjectRepo
from app.modules.projects.ports import ProjectRepoPort

def get_project_repo(db: AsyncSession = Depends(get_db)) -> ProjectRepoPort:
    return SqlAlchemyProjectRepo(db)