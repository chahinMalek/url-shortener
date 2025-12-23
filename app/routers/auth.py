import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.dependencies import AuthServiceDep, UserRepoDep
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from core.entities.users import User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/register",
    summary="Register a new user",
    description="Create a new user account with email and password",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "User with provided email is already registered"},
        422: {"description": "Validation error"},
    },
)
async def register(
    req: UserRegisterRequest, user_repository: UserRepoDep, auth_service: AuthServiceDep
):
    existing_user = await user_repository.get_by_email(req.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user_id = str(uuid.uuid4())
    password_hash = auth_service.hash_password(req.password)
    user = User(
        user_id=user_id,
        email=req.email,
        password_hash=password_hash,
        permissions=[],
        is_active=True,
        created_at=datetime.now(UTC),
    )
    created_user = await user_repository.add(user)
    return UserResponse(
        user_id=created_user.user_id,
        email=created_user.email,
        is_active=created_user.is_active,
        created_at=created_user.created_at,
        last_login=created_user.last_login,
    )


@router.post(
    "/login",
    summary="Login user",
    description="Authenticate user and return JWT access token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Authentication successful"},
        401: {"description": "Incorrect email or password"},
        403: {"description": "Account is inactive"},
        422: {"description": "Validation error"},
    },
)
async def login(body: UserLoginRequest, user_repository: UserRepoDep, auth_service: AuthServiceDep):
    user = await user_repository.get_by_email(body.email)
    if not user or not auth_service.verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # update last login
    user.last_login = datetime.now(UTC)
    await user_repository.update(user)

    # create access token
    access_token = auth_service.create_access_token(sub=user.user_id, email=user.email)
    return TokenResponse(access_token=access_token)
