from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.models.project import Project
from app.modules.projects.ports import ProjectRepoPort

@dataclass(frozen=True)
class ListProjectsInput:
    q: Optional[str] = None
    page: int = 1
    limit: int = 20

class ListProjectsUseCase:
    def __init__(self, repo: ProjectRepoPort):
        self.repo = repo

    async def execute(self, data: ListProjectsInput) -> tuple[list[Project], int]:
        return await self.repo.list(
            q=data.q,
            page=data.page,
            limit=data.limit,
            with_tags=True
        )