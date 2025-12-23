from datetime import datetime

from fastapi import APIRouter, status

from app.dependencies import CurrentUserDep
from app.schemas import ShortenRequest, ShortenResponse

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


@router.get(
    "/{short_url}",
    summary="Retrieves the original URL from the specified short URL",
    status_code=status.HTTP_200_OK,
)
async def retrieve(short_url: str):
    # TODO: Implement URL retrieval logic
    return {}
