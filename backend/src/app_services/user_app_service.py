from typing import Optional
from fastapi import HTTPException, status

from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.schemas.user import UserCreate, UserLogin, UserUpdate, Token, User
from src.models.user import User

class UserAppService:
    def __init__(self, user_service: UserService, auth_service: AuthService):
        self.user_service = user_service
        self.auth_service = auth_service

    def register_user(self, user: UserCreate) -> User:
        return self.user_service.create_user(user)

    def login(self, user_login: UserLogin) -> Token:
        user = self.user_service.authenticate_user(email=user_login.email, password=user_login.password)
        access_token = self.auth_service.create_access_token(user.id)
        refresh_token = self.auth_service.create_refresh_token(user.id)
        self.user_service.update_refresh_token(user.id, refresh_token)

        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    def refresh_token(self, refresh_token: str) -> Token:
        token_data = self.auth_service.verify_token(refresh_token, "refresh")
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )

        user_id = int(token_data.sub)
        new_access_token = self.auth_service.create_access_token(user_id)
        new_refresh_token = self.auth_service.create_refresh_token(user_id)

        self.user_service.update_refresh_token(user_id, new_refresh_token)

        return Token(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")

    def get_current_user(self, token: str) -> Optional[User]:
        token_data = self.auth_service.verify_token(token, "access")
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        user = self.user_service.get_user(int(token_data.sub))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        return user

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        return self.user_service.update_user(user_id, user_update)