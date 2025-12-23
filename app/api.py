from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, status

from app.container import db_service, settings
from app.dependencies.types import CurrentUserDep
from app.routes import auth as auth_router
from app.schemas import ShortenRequest, ShortenResponse


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


@app.put(
    "/api/v1/shorten",
    summary="Shorten a URL specified in the request body",
    description="Create a shortened URL from a long URL. Requires authentication.",
    response_model=ShortenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "URL successfully shortened"},
        401: {"description": "Unauthorized - Missing or invalid credentials"},
        403: {"description": "Forbidden - Insufficient permissions"},
    },
)
async def shorten(request: ShortenRequest, user: CurrentUserDep):
    # TODO: Implement actual URL shortening logic using hashing service
    # For now, return a mock response
    short_code = "xy725ab"

    return ShortenResponse(
        long_url=str(request.long_url),
        short_url=short_code,
        created_at=datetime.utcnow(),
        is_active=True,
    )


@app.get(
    "/api/v1/{short_url}",
    summary="Retrieves the original URL from the specified short URL",
    status_code=status.HTTP_200_OK,
)
async def retrieve(short_url: str):
    # TODO: Implement URL retrieval logic
    return {}
