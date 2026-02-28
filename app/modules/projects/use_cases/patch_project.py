from __future__ import annotations

from dataclasses import dataclass

from app.models.project import Project
from app.modules.projects.ports import ProjectRepoPort
from app.schemas.project import ProjectUpdate


@dataclass(frozen=True)
class PatchProjectInput:
    slug: str
    payload: ProjectUpdate


class PatchProjectUseCase:
    def __init__(self, repo: ProjectRepoPort):
        self.repo = repo

    async def execute(self, data: PatchProjectInput) -> Project | None:
        return await self.repo.update_by_slug(slug=data.slug, payload=data.payload)