from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from app.core.config import settings

def require_admin(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    if not x_api_key or x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")