from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import app_settings
from db.database import get_session
from schemas import user_schema
from schemas.user_schema import Token, User
from services import auth
from services.auth import get_current_user
from services.file_storage_crud import user_crud

user_router = APIRouter()


async def get_token(db: AsyncSession, username: str, password: str) -> Any:
    verify_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = await user_crud.get_by_name(db, username)
    if not user:
        raise verify_exception
    verify = await auth.authenticate_user(user, password)
    if not verify:
        raise verify_exception
    access_token_expires = timedelta(
        minutes=app_settings.access_token_expire_minutes
    )
    access_token = await auth.create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post(
    "/register",
    response_model=user_schema.User,
    status_code=status.HTTP_201_CREATED,
    description="Create new user.",
)
async def create_user(
    link_in: user_schema.UserCreate,
    db: AsyncSession = Depends(get_session),
):
    return await user_crud.create(db, obj_in=link_in)


@user_router.post("/auth", response_model=Token)
async def login_for_access_token(
    user_in: user_schema.UserInDB,
    db: AsyncSession = Depends(get_session),
):
    return await get_token(db, user_in.name, user_in.password)


@user_router.post("/auth-form", response_model=Token)
async def login_for_access_token_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_session),
):
    return await get_token(db, form_data.username, form_data.password)


@user_router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user
