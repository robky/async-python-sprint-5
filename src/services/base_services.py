from abc import ABC
from typing import Any, Generic, Type, TypeVar

from aiofiles import open
from asyncpg.exceptions import UniqueViolationError
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class Repository(ABC):
    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDB(
    Repository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def ping(self, db: AsyncSession) -> bool:
        statement = select(self._model).limit(1)
        try:
            await db.execute(statement=statement)
        except Exception:
            return False
        return True

    async def assembly_before_creation(
        self,
        db: AsyncSession,
        in_file: UploadFile,
        path: str,
        author_id: int,
        in_folder: str,
    ) -> ModelType | None:
        file_obj_in = {
            "name": in_file.filename,
            "path": path,
            "size": in_file.size,
            "author_id": author_id,
        }
        result = await self.create(db, obj_in=file_obj_in)
        if result is None:
            return None
        async with open(in_folder + str(result.id), "wb") as out_file:
            while content := await in_file.read(1024):
                await out_file.write(content)
        return result

    async def get(self, db: AsyncSession, id: int | str) -> ModelType | None:
        statement = select(self._model).where(self._model.id == id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_by_name(
        self, db: AsyncSession, name: str
    ) -> ModelType | None:
        statement = select(self._model).where(self._model.name == name)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip=0, limit=100
    ) -> list[ModelType]:
        statement = select(self._model).offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def get_files_by_user(
        self, db: AsyncSession, user_id: int
    ) -> list[ModelType]:
        statement = select(self._model).where(self._model.author_id == user_id)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def get_id_by_id_and_user(
        self, db: AsyncSession, id: str, user_id: int
    ) -> ModelType | None:
        statement = select(self._model).where(
            (self._model.id == id) & (self._model.author_id == user_id)
        )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_id_by_path_and_user(
        self, db: AsyncSession, path: str, user_id: int
    ) -> ModelType | None:
        statement = select(self._model).where(
            (self._model.path == path) & (self._model.author_id == user_id)
        )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def create(
        self, db: AsyncSession, *, obj_in: CreateSchemaType
    ) -> ModelType | None:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        try:
            await db.commit()
        except IntegrityError as e:
            if e.orig.__cause__.__class__ == UniqueViolationError:
                return None
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        statement = (
            update(self._model)
            .where(self._model.id == db_obj.id)
            .values(**obj_in_data)
        )
        await db.execute(statement=statement)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
    ) -> None:
        statement = delete(self._model).where(self._model.id == db_obj.id)
        await db.execute(statement=statement)
        await db.commit()
