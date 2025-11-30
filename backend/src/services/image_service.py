import io
import base64
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImageService:
    """Service for image preprocessing and validation."""
    
    # Configurações padrão
    SUPPORTED_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP'}
    MAX_DIMENSION = 4096  # 4K resolution
    MIN_DIMENSION = 32    # Minimum reasonable size
    
    def validate_image(self, image_data: bytes) -> Tuple[bool, Optional[str]]:
        """
        Valida se os dados da imagem são válidos e suportados.
        
        Args:
            image_data: Binary image data
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Validar formato
            if image.format not in self.SUPPORTED_FORMATS:
                return False, f"Formato não suportado: {image.format}. Use {', '.join(self.SUPPORTED_FORMATS)}"
            
            # Validar dimensões
            width, height = image.size
            if width > self.MAX_DIMENSION or height > self.MAX_DIMENSION:
                return False, f"Imagem muito grande: {width}x{height}. Máximo: {self.MAX_DIMENSION}px"
            
            if width < self.MIN_DIMENSION or height < self.MIN_DIMENSION:
                return False, f"Imagem muito pequena: {width}x{height}. Mínimo: {self.MIN_DIMENSION}px"
            
            logger.debug(f"Image validated: {image.format}, {width}x{height}, mode={image.mode}")
            return True, None
            
        except Exception as e:
            return False, f"Erro ao validar imagem: {str(e)}"
    
    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        """
        Pré-processa a imagem: valida, converte para RGB.
        
        Args:
            image_data: Binary image data
            
        Returns:
            np.ndarray: Image as numpy array in RGB format
            
        Raises:
            ValueError: If image is invalid
        """
        try:
            # Validar imagem
            is_valid, error_msg = self.validate_image(image_data)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Carregar imagem
            image = Image.open(io.BytesIO(image_data))
            
            # Converter para RGB se necessário
            if image.mode != 'RGB':
                logger.debug(f"Converting image from {image.mode} to RGB")
                image = image.convert('RGB')
            
            # Converter para numpy array
            image_array = np.array(image)
            
            logger.debug(f"Image preprocessed: shape={image_array.shape}, dtype={image_array.dtype}")
            return image_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise ValueError(f"Erro ao processar imagem: {str(e)}")
    
    def resize_image(self, image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        """
        Redimensiona a imagem para o tamanho especificado.
        
        Args:
            image: Image as numpy array
            size: Target size as (width, height)
            
        Returns:
            np.ndarray: Resized image with batch dimension
        """
        try:
            resized = cv2.resize(image, size, interpolation=cv2.INTER_LINEAR)
            return np.expand_dims(resized, axis=0)
        except Exception as e:
            raise ValueError(f"Erro ao redimensionar imagem: {str(e)}")
    
    def convert_to_rgb(self, image: np.ndarray) -> np.ndarray:
        """
        Converte a imagem para RGB se necessário.
        
        Args:
            image: Image as numpy array
            
        Returns:
            np.ndarray: Image in RGB format
        """
        if len(image.shape) == 2:  # Grayscale
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:  # RGBA
            return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        return image