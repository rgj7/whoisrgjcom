from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentUser, create_access_token
from src.auth.exceptions import InvalidCredentials
from src.auth.schemas import LoginRequest, LoginResponse, UserResponse
from src.auth.service import get_user_by_username, verify_password
from src.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or missing token"},
    },
)
async def get_current_user_info(user: CurrentUser):
    return user


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login and receive a JWT token",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"},
    },
)
async def login(data: LoginRequest, db: DbSession):
    user = await get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.hashed_password):
        raise InvalidCredentials()

    token = create_access_token(str(user.id))
    return LoginResponse(access_token=token)
