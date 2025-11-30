from typing import Optional
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserUpdate
from src.core.exceptions import ServiceError
from src.models.user import User

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user: UserCreate) -> User:
        existing_user = self.user_repository.getUserByEmail(user.email)
        if existing_user:
            raise ServiceError("E-mail já registrado")
            
        return self.user_repository.create(user)

    def get_user(self, user_id: int) -> Optional[User]:
        return self.user_repository.get_by_id(user_id)

    def getUserByEmail(self, email: str) -> Optional[User]:
        return self.user_repository.getUserByEmail(email)

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.get_user(user_id)
        if not user:
            raise ServiceError("Usuário não encontrado")
            
        if user_data.email and user_data.email != user.email:
            existing_user = self.getUserByEmail(user_data.email)
            if existing_user:
                raise ServiceError("E-mail já está em uso")
                
        updated_user = self.user_repository.update(user_id, user_data)
        if not updated_user:
            raise ServiceError("Falha ao atualizar usuário")
            
        return updated_user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            raise ServiceError("Usuário não encontrado")
            
        if not self.user_repository.delete(user_id):
            raise ServiceError("Falha ao remover usuário")
            
        return True

    def verify_password(self, user: User, password: str) -> bool:
        return self.user_repository.verify_password(user, password)

    def update_refresh_token(self, user_id: int, refresh_token: str) -> None:
        self.user_repository.update_refresh_token(user_id, refresh_token)

    def authenticate_user(self, email: str, password: str) -> User:
        user = self.getUserByEmail(email)
        if not user:
            raise ServiceError("E-mail ou senha incorretos")
        
        if not self.verify_password(user, password):
            raise ServiceError("E-mail ou senha incorretos")
        
        if not user.is_active:
            raise ServiceError("Usuário inativo")
        
        return user