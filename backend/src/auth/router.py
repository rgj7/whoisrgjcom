from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import create_access_token
from src.auth.exceptions import InvalidCredentials
from src.auth.schemas import LoginRequest, LoginResponse, UserCreate, UserResponse
from src.auth.service import create_user, get_user_by_username, verify_password
from src.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        status.HTTP_409_CONFLICT: {"description": "Username or email already exists"},
    },
)
async def register(data: UserCreate, db: DbSession):
    from sqlalchemy.exc import IntegrityError

    try:
        user = await create_user(db, data)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )
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
