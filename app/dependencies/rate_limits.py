from fastapi import Request
from fastapi.security import HTTPBearer

from app.dependencies.services import get_auth_service

security = HTTPBearer()


async def rate_limit_identifier(request: Request) -> str:
    user_id = "anonymous"
    auth_service = get_auth_service()

    # user extraction
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = auth_service.decode_access_token(token, verify_exp=False)
            if payload:
                user_id = payload.sub
        except Exception:
            pass  # keep user_id as "anonymous" on failure

    # ip extraction
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    else:
        ip = request.client.host or "unknown"
    return f"{ip}:{user_id}"
