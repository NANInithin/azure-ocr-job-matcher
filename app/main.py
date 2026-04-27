from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.documents import router as documents_router
from app.api.routes.jobs import router as jobs_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(documents_router)
app.include_router(jobs_router)