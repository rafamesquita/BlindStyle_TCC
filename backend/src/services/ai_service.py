import base64
import time
import logging

# OTIMIZAÇÃO: Importar apenas plugins PIL necessários para evitar overhead
import PIL.Image
PIL.Image.LOAD_TRUNCATED_IMAGES = True
# Pré-registra apenas JPEG e PNG para acelerar Image.open()
from PIL import JpegImagePlugin, PngImagePlugin

logger = logging.getLogger(__name__)

from src.schemas.description import ClothingFeatures, FeatureExtractionResponse
from src.utils.description_formatter import generate_description_from_features
from src.services.file_service import FileService
from src.services.image_service import ImageService

from modules import FeatureExtractor

class AIService:
    def __init__(self, feature_extractor: FeatureExtractor, file_service: FileService, image_service: ImageService):
        self.extractor = feature_extractor
        self.file_service = file_service
        self.image_service = image_service
        
        
    
    def extract_features_from_base64(self, image_base64: str) -> FeatureExtractionResponse:
        start_total = time.time()
        logger.info("[TIMER] Starting AI service feature extraction")
        
        try:
            start_decode = time.time()
            image_data = base64.b64decode(image_base64)
            elapsed_decode = time.time() - start_decode
            logger.info(f"[TIMER]   Base64 decode: {elapsed_decode:.3f}s")
            
            # Validar imagem antes de processar
            start_validate = time.time()
            is_valid, error_msg = self.image_service.validate_image(image_data)
            if not is_valid:
                return FeatureExtractionResponse(
                    success=False,
                    description=f"Imagem inválida: {error_msg}"
                )
            elapsed_validate = time.time() - start_validate
            logger.info(f"[TIMER]   Image validation: {elapsed_validate:.3f}s")
            
            # Use FileService context manager for automatic cleanup
            with self.file_service.create_temp_image_file(image_data) as image_path:
                start_file_ops = time.time()
                elapsed_file_ops = time.time() - start_file_ops
                logger.info(f"[TIMER]   File operations (managed): {elapsed_file_ops:.3f}s")
                
                #TODO USE img preprocess
                start_gemini = time.time()
                result = self.extractor.extract_features_in_memory(image_path.parent)
                elapsed_gemini = time.time() - start_gemini
                logger.info(f"[TIMER]   Gemini API call: {elapsed_gemini:.3f}s")
                
                if not result:
                    return FeatureExtractionResponse(
                        success=False,
                        description="Falha ao extrair features da imagem"
                    )
                
                first_key = list(result.keys())[0]
                features_data = result[first_key]
                
                if "error" in features_data:
                    return FeatureExtractionResponse(
                        success=False,
                        description=features_data.get("error"),
                    )
                
                start_parse = time.time()
                features = ClothingFeatures(**features_data)
                elapsed_parse = time.time() - start_parse
                logger.info(f"[TIMER]   Parse features: {elapsed_parse:.3f}s")
                
                start_description = time.time()
                description = generate_description_from_features(features.model_dump())
                elapsed_description = time.time() - start_description
                logger.info(f"[TIMER]   Generate description: {elapsed_description:.3f}s")
                
                elapsed_total = time.time() - start_total
                logger.info(f"[TIMER] TOTAL AI service: {elapsed_total:.3f}s")
                
                return FeatureExtractionResponse(
                    success=True,
                    features = features,
                    description = description
                )
                
        except Exception as e:
            return FeatureExtractionResponse(
                success=False,
                description=f"Erro ao processar imagem: {str(e)}"
            )
