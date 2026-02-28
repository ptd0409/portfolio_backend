from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from app.models.project import Project
from app.modules.projects.ports import ProjectRepoPort
from app.schemas.project import ProjectCreate

@dataclass(frozen=True)
class CreateProjectInput:
    payload: ProjectCreate

class CreateProjectUseCase:
    def __init__(self, repo: ProjectRepoPort):
        self.repo =repo

    async def execute(self, data: CreateProjectInput) -> Project:
        slug = data.payload.slug.strip()

        if await self.repo.exists_by_slug(slug=slug):
            raise ValueError("SLUG_EXISTS")
        
        try:
            return await self.repo.create(payload=data.payload)
        except IntegrityError:
            raise ValueError("SLUG_EXISTS")