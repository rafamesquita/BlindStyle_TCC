from src.services.image_service import ImageService
from src.services.ai_service import AIService
from src.schemas.description import (
  FeatureExtractionRequest, 
  FeatureExtractionResponse
)

class DescriptionAppService:
    def __init__(self, image_service: ImageService, ai_service: AIService):
        self.image_service = image_service
        self.ai_service = ai_service

    def extract_clothing_features(self, request: FeatureExtractionRequest) -> FeatureExtractionResponse:
        if not request.image_base64:
            return FeatureExtractionResponse(
                success=False,
                description="Forneça image_base64 ou image_url"
            )

        return self.ai_service.extract_features_from_base64(
            request.image_base64
        )