import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi_limiter.depends import RateLimiter

from app.container import get_settings
from app.dependencies.types import CurrentUserDep, HashingServiceDep, UrlClassifierDep, UrlRepoDep
from app.schemas import ShortenRequest, ShortenResponse
from core.entities.url import SafetyStatus, Url
from core.services.classification import ClassificationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/url", tags=["URL"])


@router.put(
    "/shorten",
    summary="Shorten a URL specified in the request body",
    description="Create a shortened URL from a long URL. Requires authentication.",
    response_model=ShortenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "URL successfully shortened"},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized - Missing or invalid credentials"
        },
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden - Insufficient permissions"},
        status.HTTP_409_CONFLICT: {"description": "Code collision detected."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "URL rejected - potentially malicious"
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Rate limit reached - too many requests"
        },
    },
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def shorten(
    request: ShortenRequest,
    user: CurrentUserDep,
    hashing_service: HashingServiceDep,
    url_repo: UrlRepoDep,
    classifier: UrlClassifierDep,
):
    long_url = str(request.long_url)
    settings = get_settings()

    # Tier 1: Fast ML classification (if enabled)
    safety_status = SafetyStatus.PENDING
    threat_score: float | None = None
    classifier_version: str | None = None

    if settings.classifier_enabled:
        try:
            result = await classifier.classify(long_url)
            safety_status = result.status
            threat_score = result.threat_score
            classifier_version = result.classifier_version

            if result.is_malicious:
                logger.warning(
                    "Rejected malicious URL",
                    extra={
                        "url": long_url,
                        "threat_score": threat_score,
                        "classifier": classifier_version,
                        "user_id": user.user_id,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="URL rejected - potentially malicious",
                )
        except ClassificationError as e:
            # Log but don't block on classification errors - fail open
            logger.error(
                "Classification failed, proceeding with PENDING status",
                extra={"url": long_url, "error": str(e)},
            )

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
        is_active=True,
        safety_status=safety_status,
        threat_score=threat_score,
        classifier_version=classifier_version,
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
    responses={
        status.HTTP_302_FOUND: {"description": "Found requested URL"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid short URL"},
        status.HTTP_404_NOT_FOUND: {"description": "Requested URL not found"},
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Rate limit reached - too many requests"
        },
    },
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def retrieve(
    short_url: str,
    url_repo: UrlRepoDep,
    hashing: HashingServiceDep,
):
    if not hashing.validate_hash(short_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid short URL")
    url = await url_repo.get_by_code(short_url)
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    response = RedirectResponse(
        url=url.long_url,
        status_code=status.HTTP_302_FOUND,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",  # HTTP/1.0 compatibility
        },
    )
    return response
