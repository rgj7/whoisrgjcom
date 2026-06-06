from datetime import UTC
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_utils import decode_token
from src.auth.exceptions import InvalidCredentials, Unauthorized
from src.auth.models import User
from src.auth.service import get_user_by_id
from src.database import get_db

bearer_scheme = HTTPBearer()
optional_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Decode JWT from Authorization: Bearer <token> header and return the user."""
    payload = decode_token(credentials.credentials)

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidCredentials()

    user = await get_user_by_id(db, UUID(user_id))
    if not user:
        raise Unauthorized()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    """Return the current user when a valid Bearer token is present; otherwise None."""
    if credentials is None:
        return None

    try:
        payload = decode_token(credentials.credentials)
    except InvalidCredentials:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        return await get_user_by_id(db, UUID(user_id))
    except ValueError:
        return None


OptionalCurrentUser = Annotated[User | None, Depends(get_optional_current_user)]


def create_access_token(user_id: str, minutes: int | None = None) -> str:
    """Create a JWT access token for the given user ID."""
    from datetime import datetime, timedelta
    from uuid import uuid4

    import jwt

    from src.auth.config import auth_settings

    exp_minutes = minutes or auth_settings.JWT_EXP_MINUTES
    expire = datetime.now(UTC) + timedelta(minutes=exp_minutes)
    return jwt.encode(
        {
            "sub": user_id,
            "exp": expire,
            "jti": str(uuid4()),
        },
        auth_settings.JWT_SECRET,
        algorithm=auth_settings.JWT_ALG,
    )
