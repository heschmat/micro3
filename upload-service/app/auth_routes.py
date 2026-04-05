from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.config import settings
from app.deps import get_db
from app.models import User
from app.schemas import (
    AuthMessageResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def serialize_user(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
    )


@router.post("/register", response_model=UserResponse)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    """
    existing_user = db.query(User).filter(User.email == payload.email).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return serialize_user(user)


@router.post("/login", response_model=UserResponse)
def login_user(
    payload: UserLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and issue an access token in an HTTP-only cookie.
    """
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # switch to True behind HTTPS in production
        samesite="lax",
        max_age=settings.JWT_EXPIRE_MINUTES * 60,
    )

    return serialize_user(user)


@router.post("/logout", response_model=AuthMessageResponse)
def logout_user(response: Response):
    """
    Log out by clearing the access token cookie.
    """
    response.delete_cookie("access_token")

    return AuthMessageResponse(message="Logged out")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Return the currently authenticated user.
    """
    return serialize_user(current_user)
