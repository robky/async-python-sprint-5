from models.file_model import File as FileModel
from models.user_model import User as UserModel
from schemas.file_schema import FileCreate, FileUpdate
from schemas.user_schema import UserCreate, UserUpdate
from services.base_services import RepositoryDB


class RepositoryFile(RepositoryDB[FileModel, FileCreate, FileUpdate]):
    pass


class RepositoryUser(RepositoryDB[UserModel, UserCreate, UserUpdate]):
    pass


file_crud = RepositoryFile(FileModel)
user_crud = RepositoryUser(UserModel)
