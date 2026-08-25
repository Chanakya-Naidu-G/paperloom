from datetime import datetime, timedelta, timezone
import os

import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

_ENV = os.getenv("ENV", "development").lower()
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    if _ENV == "production":
        raise RuntimeError("SECRET_KEY must be set in production")
    SECRET_KEY = "insecure-dev-secret-change-me"

ALGORITHM = "HS256"

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
    )
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 10080


class AuthError(Exception):
    pass


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    payload = {
        "sub": str(user_id),
        "exp": expires,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError("Invalid token") from exc

    subject = payload.get("sub")

    if subject is None:
        raise AuthError("Invalid token payload")

    try:
        return int(subject)
    except (TypeError, ValueError) as exc:
        raise AuthError("Invalid token payload") from exc
