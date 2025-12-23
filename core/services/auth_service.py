from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from jose import JWTError, jwt

from app.schemas.auth import TokenPayload
from infra.config import Settings


class AuthService:
    def __init__(self, settings: Settings):
        self._token_expiration = settings.access_token_expire_minutes
        self._algorithm = settings.algorithm
        self._secret_key = settings.secret_key
        self._hasher = PasswordHasher(
            time_cost=3,
            memory_cost=64 * 1024,  # 64 MiB
            parallelism=2,
            hash_len=32,
            salt_len=16,
        )

    def hash_password(self, password: str) -> str:
        if not password:
            raise ValueError("Password must not be empty")
        if len(password) > 1024:
            raise ValueError("Password too long")
        return self._hasher.hash(password)

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        try:
            return self._hasher.verify(password_hash, plain_password)
        except (VerifyMismatchError, VerificationError):
            return False

    def create_access_token(self, sub: str, email: str) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self._token_expiration)
        payload = TokenPayload(sub=sub, email=email, exp=expire)
        return jwt.encode(
            claims=payload.model_dump(mode="json"),
            key=self._secret_key,
            algorithm=self._algorithm,
        )

    def decode_access_token(self, token: str) -> TokenPayload | None:
        try:
            payload_dict = jwt.decode(
                token=token,
                key=self._secret_key,
                algorithms=[self._algorithm],
            )
            return TokenPayload(**payload_dict)
        except (JWTError, ValueError):
            return None
