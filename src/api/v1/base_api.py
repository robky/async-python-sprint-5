from fastapi import APIRouter

from api.v1.file_storage_api import file_router
from api.v1.user_api import user_router

api_router = APIRouter()
api_router.include_router(file_router, prefix="/files", tags=["File Storage"])
api_router.include_router(user_router, prefix="/user", tags=["Users"])
