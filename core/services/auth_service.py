from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.schemas.auth import TokenPayload
from infra.config import Settings


class AuthService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, sub: str, email: str) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self.settings.access_token_expire_minutes)
        payload = TokenPayload(sub=sub, email=email, exp=expire)
        encoded_jwt = jwt.encode(
            claims=payload.model_dump(mode="json"),
            key=self.settings.secret_key,
            algorithm=self.settings.algorithm,
        )
        return encoded_jwt

    def decode_access_token(self, token: str) -> TokenPayload | None:
        try:
            payload_dict = jwt.decode(
                token=token,
                key=self.settings.secret_key,
                algorithms=[self.settings.algorithm],
            )
            return TokenPayload(**payload_dict)
        except (JWTError, ValueError):
            return None
