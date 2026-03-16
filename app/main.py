from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limit import limiter

app = FastAPI(title=settings.APP_NAME)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(v1_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(v1_router, prefix="/api/v1")

origins = [
    "https://blooperry.com",
    "https://www.blooperry.com",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")