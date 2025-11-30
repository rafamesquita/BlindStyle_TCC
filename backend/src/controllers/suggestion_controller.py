from fastapi import APIRouter, Depends, HTTPException
from src.schemas.sugestion import SugestionResponse
from src.app_services.suggestion_app_service import SuggestionAppService
from src.core.dependencies import get_suggestion_app_service, get_current_user, get_db
from src.schemas.user import User

router = APIRouter(prefix="/suggestions", tags=["suggestions"])

@router.post("/generate", response_model=SugestionResponse)
async def generate_suggestion(
    item_id: int,
    current_user: User = Depends(get_current_user),
    app_service: SuggestionAppService = Depends(get_suggestion_app_service)
):
    """
    Gera uma sugestão com base em um item fornecido.
    """
    try:
        suggestion = await app_service.generate_suggestion(item_id, user_id=current_user.id)
        return suggestion
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
