from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status
from passlib.context import CryptContext

from src.core.config.settings import settings
from src.models.user import User, AuthProvider
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserLogin, TokenPayload, TokenResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def _create_token(self, user_id: int, expires_delta: timedelta, token_type: str = "access") -> str:
        expire = datetime.utcnow() + expires_delta
        to_encode = {"sub": str(user_id), "exp": expire, "token_type": token_type}
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_access_token(self, user_id: int) -> str:
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        return self._create_token(user_id, expires_delta, "access")

    def create_refresh_token(self, user_id: int) -> str:
        expires_delta = timedelta(days=self.refresh_token_expire_days)
        return self._create_token(user_id, expires_delta, "refresh")

    def _get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_user(self, user_data: UserCreate) -> User:
        existing_user = self.user_repository.getUserByEmail(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
            
        return self.user_repository.create(user_data)

    def authenticate_user(self, login_data: UserLogin) -> TokenResponse:
        user = self.user_repository.getUserByEmail(login_data.email)
        if not user or user.auth_provider != AuthProvider.LOCAL:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
            
        if not self._verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
            
        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)
        
        user.last_login = datetime.utcnow()
        self.user_repository.update(user.id, {"last_login": user.last_login})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    def verify_token(self, token: str, token_type: str = "access") -> TokenPayload:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            token_data = TokenPayload(**payload)
            
            if token_data.token_type != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido para esta operação"
                )
                
            return token_data
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        token_data = self.verify_token(refresh_token, "refresh")
        
        user = self.user_repository.get_by_id(int(token_data.sub))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
        
        access_token = self.create_access_token(user.id)
        new_refresh_token = self.create_refresh_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    def validate_token(self, token: str) -> User:
        token_data = self.verify_token(token, "access")
        
        user = self.user_repository.get_by_id(int(token_data.sub))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo"
            )
        
        return user