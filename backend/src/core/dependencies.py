from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from src.app_services.description_app_service import DescriptionAppService
from src.services.ai_service import AIService
from src.services.item_service import ItemService
from src.core.db import get_db
from src.core.di.container import Container

from src.models.user import User

from src.repositories.user_repository import UserRepository

from src.services.auth_service import AuthService

from src.app_services.item_app_service import ItemAppService
from src.app_services.user_app_service import UserAppService
from src.app_services.suggestion_app_service import SuggestionAppService

security = HTTPBearer(scheme_name="bearerAuth", description="Insira o token JWT obtido no endpoint de login", auto_error=True)

container = Container()

def get_container() -> Container:
    return container

# ============ Repositórios ============
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return container.user_repository(db=db)

# ============ Serviços ============
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = container.user_repository(db=db)
    return container.auth_service(user_repository=user_repo)

# ============ App Services ============
def get_user_app_service(db: Session = Depends(get_db)) -> UserAppService:
    user_repo = container.user_repository(db=db)
    user_service = container.user_service(user_repository=user_repo)
    auth_service = container.auth_service(user_repository=user_repo)
    return container.user_app_service(user_service=user_service, auth_service=auth_service)

def get_item_app_service(db: Session = Depends(get_db)) -> ItemAppService:
    item_repo = container.item_repository(db=db)
    item_service = container.item_service(repository=item_repo)
    return container.item_app_service(item_service=item_service)

def get_description_app_service() -> DescriptionAppService:
    return container.description_app_service()

def get_suggestion_app_service(db: Session = Depends(get_db)) -> SuggestionAppService:
    return container.suggestion_app_service(db=db)

# ============ Autenticação ============
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), auth_service: AuthService = Depends(get_auth_service)) -> User:
    try:
        token = credentials.credentials 
        return auth_service.validate_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )