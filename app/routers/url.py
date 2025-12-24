from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from app.dependencies.types import CurrentUserDep, HashingServiceDep, UrlRepoDep
from app.schemas import ShortenRequest, ShortenResponse
from core.entities.url import Url

router = APIRouter(prefix="/api/v1/url", tags=["URL"])


@router.put(
    "/shorten",
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
async def shorten(
    request: ShortenRequest,
    user: CurrentUserDep,
    hashing_service: HashingServiceDep,
    url_repo: UrlRepoDep,
):
    long_url = str(request.long_url)
    short_code = hashing_service.generate_hash(long_url)

    # check if already exists
    existing = await url_repo.get_by_code(short_code)
    if existing:
        # fixme: returning error on collision
        if existing.long_url != long_url:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Code collision detected",
            )
        return ShortenResponse(
            long_url=existing.long_url,
            short_url=existing.short_code,
            created_at=existing.created_at,
            is_active=existing.is_active,
        )
    url = Url(
        short_code=short_code,
        long_url=long_url,
        owner_id=user.user_id,
        created_at=datetime.now(UTC),
        is_active=True,
    )
    await url_repo.add(url)
    return ShortenResponse(
        long_url=url.long_url,
        short_url=url.short_code,
        created_at=url.created_at,
        is_active=url.is_active,
    )


@router.get(
    "/{short_url}",
    summary="Retrieves the original URL from the specified short URL",
    description="""
    Retrieves the original URL from the specified short URL.
    Uses HTTP 302 in the response to ensure redirect requests are not permanently cached by clients.
    This way observability is preserved and we allow future destination changes.
    """,
    status_code=status.HTTP_302_FOUND,
)
async def retrieve(
    short_url: str,
    url_repo: UrlRepoDep,
    hashing: HashingServiceDep,
):
    if not hashing.validate_hash(short_url):
        raise HTTPException(status_code=404, detail="Invalid short URL")
    url = await url_repo.get_by_code(short_url)
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    response = RedirectResponse(
        url=url.long_url,
        status_code=status.HTTP_302_FOUND,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",  # HTTP/1.0 compatibility
        },
    )
    return response
