from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import Depends, FastAPI, status
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from app.container import config, db_service
from app.dependencies.rate_limits import rate_limit_identifier
from app.routers import auth as auth_router
from app.routers import url as url_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_service.init_db()
    redis = aioredis.from_url(config.redis_url)
    await FastAPILimiter.init(redis, identifier=rate_limit_identifier)
    yield
    await FastAPILimiter.close()
    await db_service.close()


app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    debug=config.debug,
    lifespan=lifespan,
)

app.include_router(auth_router.router)
app.include_router(url_router.router)


@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, seconds=60))],
)
async def root():
    return {
        "message": "URL Shortener API",
        "version": config.app_version,
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Check API health status",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=3, seconds=60))],
)
def health_check():
    return {
        "status": "healthy",
        "version": config.app_version,
    }
