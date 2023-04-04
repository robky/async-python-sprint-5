from time import monotonic
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from schemas import file_schema, user_schema
from services.auth import get_current_user
from services.file_storage_crud import file_crud

file_router = APIRouter()

in_folder = "static/"


def is_valid_uuid(uuid):
    try:
        uuid_obj = UUID(uuid)
    except ValueError:
        return False
    return str(uuid_obj) == uuid


@file_router.get(
    "/ping",
    description="Ping db",
)
async def ping_db(db: AsyncSession = Depends(get_session)):
    start_time = monotonic()
    result = await file_crud.ping(db)
    work_time = float(f"{monotonic() - start_time:.2f}")
    if result:
        return {"status": "ok", "db_response_time": work_time}
    return {"status": "error", "db_response_time": None}


@file_router.get(
    "",
    response_model=file_schema.FilesUser,
    description="Retrieve files storage.",
)
async def get_files_info(
        current_user: Annotated[user_schema.UserId, Depends(get_current_user)],
        db: AsyncSession = Depends(get_session),
) -> Any:
    return {
        "account": current_user.name,
        "files": await file_crud.get_files_by_user(
            db, user_id=current_user.id
        ),
    }


@file_router.post(
    "/upload",
    response_model=file_schema.File,
    status_code=status.HTTP_201_CREATED,
    description="Upload file.",
)
async def file_upload(
        path: str,
        current_user: Annotated[user_schema.UserId, Depends(get_current_user)],
        db: AsyncSession = Depends(get_session),
        in_file: UploadFile = File(...),
):
    result = await file_crud.assembly_before_creation(
        db, in_file, path, current_user.id, in_folder)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This value is already exist",
        )
    return result


@file_router.get("/download", description="Download file.")
async def file_download(
        current_user: Annotated[user_schema.UserId, Depends(get_current_user)],
        path: str,
        db: AsyncSession = Depends(get_session),
):
    if is_valid_uuid(path):
        file_obj = await file_crud.get_id_by_id_and_user(
            db, id=path, user_id=current_user.id
        )
    else:
        file_obj = await file_crud.get_id_by_path_and_user(
            db, path=path, user_id=current_user.id
        )
    if file_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # return in_folder + str(file_obj.id)

    headers = {
        'Content-Disposition': f"attachment; filename={file_obj.name}"
    }
    return FileResponse(in_folder + str(file_obj.id), headers=headers)
