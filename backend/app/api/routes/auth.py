from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import security
from app.database.connection import get_db
from app.database.entities import User

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


class AuthRequest(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username (letters, digits, underscores)",
    )

    password: str = Field(
        min_length=6,
        max_length=128,
        description="Password (minimum 6 characters)",
    )


class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    username: str


def _authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> User | None:

    user = db.scalar(
        select(User).where(User.username == username)
    )

    if user is None:
        return None

    if not security.verify_password(
        password,
        user.hashed_password,
    ):
        return None

    return user


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: AuthRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:

    existing = db.scalar(
        select(User).where(User.username == request.username)
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already taken.",
        )

    user = User(
        username=request.username,
        hashed_password=security.hash_password(
            request.password,
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=security.create_access_token(user.id),
        username=user.username,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: AuthRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:

    user = _authenticate_user(
        db,
        request.username,
        request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )

    return TokenResponse(
        access_token=security.create_access_token(user.id),
        username=user.username,
    )
