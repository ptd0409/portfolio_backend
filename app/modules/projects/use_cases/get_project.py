from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.models.project import Project
from app.modules.projects.ports import ProjectRepoPort

@dataclass(frozen=True)
class GetProjectInput:
    slug: str

class GetProjectUseCase:
    def __init__(self, repo: ProjectRepoPort):
        self.repo = repo

    async def execute(self, data: GetProjectInput) -> Optional[Project]:
        return await self.repo.get_by_slug(slug=data.slug, with_tags=True, published_only=True)