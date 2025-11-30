import numpy as np
import io
import base64
from PIL import Image

def preprocess_image(image_bytes: bytes) -> bytes:
    try:

        image = Image.open(io.BytesIO(image_bytes))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        image_array = np.array(image)
        
        normalized_image = image_array.astype(float) / 255.0
        
        normalized_image = (normalized_image * 255).astype(np.uint8)
        img = Image.fromarray(normalized_image)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        
        return img_byte_arr.getvalue()
        
    except Exception as e:
        raise Exception(f"Erro no pré-processamento da imagem: {str(e)}")


def compress_image_to_jpeg(image_data: bytes, quality: int = 75, return_base64: bool = True) -> str | bytes:
    """
    Comprime imagem para formato JPEG com qualidade ajustável.
    
    Reduz o tamanho do payload para respostas da API. Recomendado para:
    - Endpoint de suggestions (múltiplas imagens por resposta)
    - Payloads grandes (500KB-2MB) podem ser reduzidos em 50-60%
    
    Args:
        image_data: Bytes da imagem original (JPEG, PNG, WEBP, etc)
        quality: Qualidade JPEG (1-100)
            - 85: Alta qualidade, ~30-40% redução
            - 75: Balanceado, ~50-60% redução (RECOMENDADO)
            - 60: Mais comprimido, ~70-75% redução
        return_base64: Se True, retorna string base64. Se False, retorna bytes
        
    Returns:
        String base64 da imagem comprimida (se return_base64=True)
        ou bytes da imagem comprimida (se return_base64=False)
        
    Raises:
        Exception: Se houver erro ao comprimir a imagem
        
    Performance:
        ~10-50ms adicional por imagem (aceitável vs ganho de bandwidth)
    """
    try:
        # Carregar imagem
        img = Image.open(io.BytesIO(image_data))
        
        # Converter para RGB se necessário (JPEG não suporta transparência)
        if img.mode in ('RGBA', 'P', 'LA'):
            # Criar fundo branco para imagens com transparência
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Comprimir para JPEG em buffer
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        # Retornar base64 ou bytes
        compressed_bytes = buffer.getvalue()
        
        if return_base64:
            return base64.b64encode(compressed_bytes).decode('utf-8')
        else:
            return compressed_bytes
        
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Erro detalhado ao comprimir imagem: {type(e).__name__}: {str(e)}")
        raise Exception(f"Erro ao comprimir imagem: {str(e)}")