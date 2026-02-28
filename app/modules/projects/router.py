from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.modules.projects.deps import get_project_repo
from app.modules.projects.ports import ProjectRepoPort
from app.modules.projects.use_cases.list_projects import ListProjectsInput, ListProjectsUseCase
from app.modules.projects.use_cases.get_project import GetProjectInput, GetProjectUseCase
from app.modules.projects.use_cases.create_project import CreateProjectInput, CreateProjectUseCase

from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.project import ProjectCreate, ProjectRead, ProjectListItem, ProjectUpdate

from app.modules.projects.use_cases.patch_project import PatchProjectInput, PatchProjectUseCase

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=ApiResponse[list[ProjectListItem]])
async def list_projects_endpoint(
    q: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    repo: ProjectRepoPort = Depends(get_project_repo)
):
    uc = ListProjectsUseCase(repo)
    items, total = await uc.execute(ListProjectsInput(q=q, page=page, limit=limit))

    return ApiResponse(
        data=items,
        meta=PaginationMeta(page=page, limit=limit, total=total),
        message="success"
    )

@router.get("/{slug}", response_model=ApiResponse[ProjectRead])
async def get_project_detail_endpoint(
    slug: str,
    repo: ProjectRepoPort = Depends(get_project_repo)
):
    uc = GetProjectUseCase(repo)
    project = await uc.execute(GetProjectInput(slug=slug))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ApiResponse(data=project, meta=None, message="success")

@router.patch("/{slug}", response_model=ApiResponse[ProjectRead])
async def patch_project_endpoint(
    slug: str,
    payload: ProjectUpdate,
    repo: ProjectRepoPort = Depends(get_project_repo)
):
    uc = PatchProjectUseCase(repo)
    project = await uc.execute(PatchProjectInput(slug=slug, payload=payload))

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ApiResponse(data=project, meta=None, message="updated")

@router.post("", response_model=ApiResponse[ProjectRead], status_code=201)
async def create_project_endpoint(
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
    return ApiResponse(data=project, meta=None, message="created")