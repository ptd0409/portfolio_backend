from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.admin_deps import require_admin
from app.modules.projects.deps import get_project_repo
from app.modules.projects.ports import ProjectRepoPort

from app.modules.projects.use_cases.create_project import CreateProjectInput, CreateProjectUseCase
from app.modules.projects.use_cases.patch_project import PatchProjectInput, PatchProjectUseCase
from app.modules.projects.use_cases.delete_project import DeleteProjectInput, DeleteProjectUseCase

from app.schemas.common import ApiResponse
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead

router = APIRouter(
    prefix="/admin/projects",
    tags=["admin-projects"],
    dependencies=[Depends(require_admin)]
)

@router.post("", response_model=ApiResponse[ProjectRead], status_code=201)
async def admin_create_project(
    payload: ProjectCreate,
    repo: ProjectRepoPort = Depends(get_project_repo)
):
    uc = CreateProjectUseCase(repo)
    try:
        project = await uc.execute(CreateProjectInput(payload=payload))
    except ValueError as e:
        if str(e) == "SLUG_EXISTS":
            raise HTTPException(status_code=409, detail="Slug already exists")
        raise
    return ApiResponse(data=project, meta=None, message="updated")

@router.patch("/{slug}", response_model=ApiResponse[ProjectRead])
async def admin_patch_project(
    slug: str,
    payload: ProjectUpdate,
    repo: ProjectRepoPort = Depends(get_project_repo)
):
    uc = PatchProjectUseCase(repo)
    project = await uc.execute(PatchProjectInput(slug=slug, payload=payload))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ApiResponse(data=project, meta=None, message="update")

@router.delete("/{slug}", status_code=204)
async def admin_delete_project(
    slug: str,
    repo: ProjectRepoPort = Depends(get_project_repo)
):
    uc = DeleteProjectUseCase(repo)
    ok = await uc.execute(DeleteProjectInput(slug=slug))
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found")
    return None