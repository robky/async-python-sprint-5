from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import app_settings
from db.database import get_session
from schemas.user_schema import TokenData, UserInDB
from services.file_storage_crud import user_crud
from services.hash_pwd import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/user/auth-form")


async def authenticate_user(user: UserInDB, password: str):
    return verify_password(password, user.password)


async def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, app_settings.secret_key, algorithm=app_settings.algorithm
    )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, app_settings.secret_key, algorithms=[app_settings.algorithm]
        )
    except JWTError:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    token_data = TokenData(username=username)

    user = await user_crud.get_by_name(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user
