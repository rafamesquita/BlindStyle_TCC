from fastapi import APIRouter, Depends, HTTPException, status

from src.core.exceptions import ServiceError
from src.core.dependencies import get_user_app_service
from src.schemas.user import UserCreate, UserLogin, Token, User
from src.app_services.user_app_service import UserAppService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, app_service: UserAppService = Depends(get_user_app_service)):
    try:
        return app_service.register_user(user)
    except ServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, app_service: UserAppService = Depends(get_user_app_service)):
    try:
        return app_service.login(login_data)
    except ServiceError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/refresh-token", response_model=Token)
def refresh_token(refresh_token: str, app_service: UserAppService = Depends(get_user_app_service)):
    try:
        return app_service.refresh_token(refresh_token)
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )