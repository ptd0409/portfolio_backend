from __future__ import annotations

from typing import Optional, Protocol

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

class ProjectRepoPort(Protocol):
    async def list(
        self,
        *,
        q: Optional[str],
        tag: Optional[str],
        page: int,
        limit: int,
        with_tags: bool = True,
        published_only: bool = False
    ) -> tuple[list[Project], int]:
        ...

    async def get_by_slug(
        self,
        *,
        slug: str,
        with_tags: bool = True,
        published_only: bool = False
    ) -> Optional[Project]:
        ...
    
    async def create(
        self,
        *,
        payload: ProjectCreate
    ) -> Project:
        ...

    async def exists_by_slug(
        self,
        *,
        slug: str,
    ) -> bool:
        ...

class ProjectRepoPort(Protocol):
    async def exists_by_slug(self, *, slug: str) -> bool: ...
    async def list(self, *, q: Optional[str], page: int, limit: int, with_tags: bool = True) -> tuple[list[Project], int]: ...
    async def get_by_slug(self, *, slug: str, with_tags: bool = True) -> Optional[Project]: ...
    async def create(self, *, payload: ProjectCreate) -> Project: ...

    async def update_by_slug(self, *, slug: str, payload: ProjectUpdate) -> Optional[Project]: ...