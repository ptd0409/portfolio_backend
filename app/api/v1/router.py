from fastapi import APIRouter

from app.modules.projects.router import router as projects_router
from app.modules.tags.router import router as tags_router
from app.modules.admin_projects.router import router as admin_projects_router
from app.modules.contact.router import router as contact_router
from app.modules.admin_uploads.router import router as admin_uploads_router
from app.modules.auth.router import router as auth_router

router = APIRouter()
router.include_router(projects_router)
router.include_router(tags_router)
router.include_router(admin_projects_router)
router.include_router(contact_router)
router.include_router(admin_uploads_router)
router.include_router(auth_router)
