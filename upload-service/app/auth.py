from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Cookie, Depends, Header, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.deps import get_db
from app.models import User

# Password hashing helper.
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Use bcrypt_sha256 instead of plain bcrypt.
# This avoids bcrypt's 72-byte password limitation by hashing first,
# then feeding the result into bcrypt.
# pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=102400,  # KB (100 MB)
    argon2__time_cost=2,
    argon2__parallelism=8,
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password before storing it.
    """
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plain text password against a stored hash.
    """
    verified, new_hash = pwd_context.verify_and_update(password, password_hash)

    if verified and new_hash:
        # save new_hash to DB here
        pass

    return verified


def create_access_token(user_id: str) -> str:
    """
    Create a signed JWT access token for the given user ID.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolve the current logged-in user from the access_token cookie.
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(
            access_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def verify_worker_token(
    x_service_token: str | None = Header(default=None),
) -> None:
    """
    Verify internal worker access using a shared secret header.

    Required request header:
    X-Service-Token: <secret>
    """
    if x_service_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
