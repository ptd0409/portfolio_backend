from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from app.api.v1.admin_deps import require_admin

router = APIRouter(
    prefix="/admin/uploads",
    tags=["admin-uploads"],
    dependencies=[Depends(require_admin)],
)

BASE_UPLOAD_DIR = Path("uploads/projects")
BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def safe_slug(value: str) -> str:
    value = (value or "").strip().lower()
    return "".join(c for c in value if c.isalnum() or c in ("-", "_"))


def save_uploaded_image(file: UploadFile, slug: str, subfolder: str) -> str:
    ext = Path(file.filename).suffix.lower() or ".png"
    allowed_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    project_dir = BASE_UPLOAD_DIR / slug / subfolder
    project_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{ext}"
    filepath = project_dir / filename
    return str(filepath), filename


@router.post("/image")
async def upload_editor_image(
    file: UploadFile = File(...),
    project_slug: str = Form(...),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    slug = safe_slug(project_slug)
    if not slug:
        raise HTTPException(status_code=400, detail="Project slug is required")

    filepath, filename = save_uploaded_image(file, slug, "content")

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    return {
        "location": f"http://127.0.0.1:8000/uploads/projects/{slug}/content/{filename}"
    }


@router.post("/cover")
async def upload_cover_image(
    file: UploadFile = File(...),
    project_slug: str = Form(...),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    slug = safe_slug(project_slug)
    if not slug:
        raise HTTPException(status_code=400, detail="Project slug is required")

    filepath, filename = save_uploaded_image(file, slug, "cover")

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    return {
        "location": f"http://127.0.0.1:8000/uploads/projects/{slug}/cover/{filename}"
    }