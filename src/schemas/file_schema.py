from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FileBase(BaseModel):
    path: str


class FileCreate(FileBase):
    pass


class FileUpdate(FileBase):
    pass


class FileInDb(FileBase):
    id: UUID
    name: str
    created_ad: datetime
    path: str
    size: int

    class Config:
        orm_mode = True


class File(FileInDb):
    pass


class FilesUser(BaseModel):
    account: str
    files: list[File]
