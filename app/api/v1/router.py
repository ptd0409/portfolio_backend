from fastapi import APIRouter

from app.api.v1.endpoints.projects import router as projects_router
from app.api.v1.endpoints.tags import router as tags_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.admin_projects import router as admin_projects_router
from app.api.v1.endpoints.admin_tags import router as admin_tags_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(projects_router)
router.include_router(tags_router)
router.include_router(admin_projects_router)
router.include_router(admin_tags_router)