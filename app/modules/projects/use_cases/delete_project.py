from __future__ import annotations

from dataclasses import dataclass
from app.modules.projects.ports import ProjectRepoPort

@dataclass(frozen=True)
class DeleteProjectInput:
    slug: str

class DeleteProjectUseCase:
    def __init__(self, repo: ProjectRepoPort):
        self.repo = repo

    async def execute(self, data: DeleteProjectInput) -> bool:
        return await self.repo.delete_by_slug(slug=data.slug)