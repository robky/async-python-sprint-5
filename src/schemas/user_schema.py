from pydantic import BaseModel, validator

from services.hash_pwd import get_password_hash


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    password: str

    @validator("password", pre=True)
    @classmethod
    def hash_password(cls, value):
        return get_password_hash(value)


class UserUpdate(UserBase):
    pass


class UserInDB(UserBase):
    password: str

    class Config:
        orm_mode = True


class User(UserBase):
    pass

    class Config:
        orm_mode = True


class UserId(User):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
