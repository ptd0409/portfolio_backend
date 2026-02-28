from fastapi import APIRouter

from app.modules.projects.router import router as projects_router
from app.modules.tags.router import router as tags_router
#from app.modules.auth.router import router as auth_router
#from app.modules.admin_prpjects.router import router as admin_projects_router
#from app.modules.admin_tags.router import router as admin_tags_router

router = APIRouter()
#router.include_router(auth_router)
router.include_router(projects_router)
router.include_router(tags_router)
#router.include_router(admin_projects_router)
#router.include_router(admin_tags_router)