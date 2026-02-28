from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class TagWithCount:
    id: int
    slug: str
    name: str
    count: int

class TagsRepoPort(Protocol):
    async def list_tags(self, q: str | None, limit: int, offset: int) -> list[TagWithCount]:
        ...