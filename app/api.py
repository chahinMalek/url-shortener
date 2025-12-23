from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from app.container import db_service, settings
from app.routers import auth as auth_router
from app.routers import url as url_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_service.init_db()
    yield
    await db_service.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(auth_router.router)
app.include_router(url_router.router)


@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
    status_code=status.HTTP_200_OK,
)
async def root():
    return {
        "message": "URL Shortener API",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Check API health status",
    status_code=status.HTTP_200_OK,
)
def health_check():
    return {
        "status": "healthy",
    }
