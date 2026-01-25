import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi_limiter.depends import RateLimiter

from app.dependencies.types import (
    ClassificationResultRepoDep,
    CurrentUserDep,
    HashingServiceDep,
    UrlClassifierDep,
    UrlRepoDep,
    UrlValidatorDep,
)
from app.schemas import ShortenRequest, ShortenResponse
from core.entities.classification_result import ClassificationResult
from core.entities.url import Url
from core.enums.safety_status import SafetyStatus
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
    classification_results_repo: ClassificationResultRepoDep,
    validator: UrlValidatorDep,
    classifier: UrlClassifierDep,
):
    long_url = str(request.long_url)

    if not validator.is_valid(long_url):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="URL rejected - invalid URL",
        )

    classification_result = None
    safety_status = SafetyStatus.PENDING
    threat_score = None
    classifier_name = None

    try:
        start_time = time.perf_counter()
        classifier_result = await classifier.classify(long_url)
        latency_ms = (time.perf_counter() - start_time) * 1000

        classification_result = ClassificationResult.from_classifier_result(
            classifier_result,
            latency_ms=latency_ms,
        )

        threat_score = classification_result.threat_score
        classifier_name = classification_result.classifier
        safety_status = classification_result.status

        if classification_result.is_malicious:
            logger.warning(
                "Rejected malicious URL",
                extra={
                    "url": long_url,
                    "threat_score": threat_score,
                    "classifier": classifier_name,
                    "user_id": user.user_id,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="URL rejected - potentially malicious",
            )

    except ClassificationError as e:
        # silent fail - log but don't block on classification errors
        logger.error(
            "Classification failed, proceeding with PENDING status",
            extra={"url": long_url, "error": str(e)},
        )

    short_code = hashing_service.generate_hash(long_url)

    # check if already exists
    url = await url_repo.get_by_code(short_code)

    # not exists - create new
    if url is None:
        url = Url(
            short_code=short_code,
            long_url=long_url,
            owner_id=user.user_id,
            is_active=True,
            safety_status=safety_status,
            threat_score=threat_score,
            classified_at=classification_result.timestamp if classification_result else None,
            classifier=classifier_name,
        )
        await url_repo.add(url)

    # exists but long_url differs
    elif url.long_url != long_url:
        # fixme: returning error on collision
        if url.long_url != long_url:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Code collision detected",
            )

    # store classification result if available
    if classification_result:
        await classification_results_repo.add(short_code, classification_result)

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
