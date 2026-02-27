from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)
app.include_router(v1_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(v1_router, prefix="/api/v1")

