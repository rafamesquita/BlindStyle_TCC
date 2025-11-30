import base64
import time
import logging
from fastapi import APIRouter, HTTPException, Depends,status

from src.core.dependencies import get_current_user
from src.app_services.description_app_service import DescriptionAppService

logger = logging.getLogger(__name__)

from src.app_services.description_app_service import DescriptionAppService
from src.schemas.description import (
  FeatureExtractionRequest,
  FeatureExtractionResponse
)
from src.core.dependencies import get_current_user, get_description_app_service
from src.models.user import User

router = APIRouter(
    prefix="/api/descriptions",
    tags=["descriptions"]
)

@router.post(
    "/extract-features/upload",
    response_model=FeatureExtractionResponse,
    summary="Extrai features via upload de arquivo",
    description="Recebe base64 da imagem para extração de features"
)
async def extract_features_from_base64(
    request: FeatureExtractionRequest,
    current_user: User = Depends(get_current_user),
    app_service: DescriptionAppService = Depends(get_description_app_service)
):
    start_total = time.time()
    logger.info(f"[TIMER] Starting extract_features for user={current_user.id}")
    
    try:
        start_decode = time.time()
        _ = base64.b64decode(request.image_base64)
        elapsed_decode = time.time() - start_decode
        logger.info(f"[TIMER] Base64 decode: {elapsed_decode:.3f}s")
        
        start_extract = time.time()
        result = app_service.extract_clothing_features(request)
        elapsed_extract = time.time() - start_extract
        logger.info(f"[TIMER] App service extraction: {elapsed_extract:.3f}s")

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.description
            )
        
        elapsed_total = time.time() - start_total
        logger.info(f"[TIMER] TOTAL extract_features: {elapsed_total:.3f}s")
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )