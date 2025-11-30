import os
import json
import re
import time
import logging
import hashlib
from pathlib import Path

# OTIMIZAÇÃO: Importar apenas plugins PIL necessários (JPEG e PNG)
import PIL.Image
from PIL import JpegImagePlugin, PngImagePlugin
PIL.Image.LOAD_TRUNCATED_IMAGES = True

# Desabilitar logging verbose do PIL
PIL_logger = logging.getLogger('PIL')
PIL_logger.setLevel(logging.WARNING)

from PIL import Image
import google.generativeai as genai
from typing import List, Dict, Union, Optional

logger = logging.getLogger(__name__)

from .config import (
    IMAGES_DIR, 
    RESPONSES_DIR, 
    FEATURE_EXTRACTION_PROMPT,
    GEMINI_API_KEY,
    LLM_MODEL
)

class FeatureExtractor:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(LLM_MODEL)
        self.prompt = FEATURE_EXTRACTION_PROMPT

    def _numeric_sort_key(self, filename: str) -> Union[int, str]:
        base = os.path.splitext(filename)[0]
        try:
            return int(base)
        except ValueError:
            return base

    def _load_images_with_names(self, folder: Path) -> List:
        parts = [self.prompt]
        files = [f for f in os.listdir(folder) if f.lower().endswith(".jpg") or f.lower().endswith(".png")]
        for file in sorted(files, key=self._numeric_sort_key):
            image_path = os.path.join(folder, file)
            try:
                img = Image.open(image_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                parts.append(f"Filename of the image below: {file} image:")
                parts.append(img)
            except Exception as e:
                print(f"Erro ao carregar imagem {file}: {e}")
        return parts

    def _extract_clean_json(self, text: str) -> str:
        """
        Extrai JSON limpo do texto da resposta do Gemini.
        Remove markdown code fences e corrige double braces.
        """
        # Remove code fences markdown
        match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        if match:
            json_text = match.group(1)
        else:
            json_text = text
        
        # Corrige double braces {{ }} -> { }
        # Gemini às vezes retorna {{...}} para template safety
        json_text = re.sub(r'\{\{', '{', json_text)
        json_text = re.sub(r'\}\}', '}', json_text)
        
        return json_text

    def extract_features(self, folder_path: Union[str, Path]) -> Optional[Dict]:
        """
        Extrai features de todas as imagens em uma pasta usando o Gemini.
        
        Args:
            folder_path: Caminho para a pasta contendo as imagens JPG
            
        Returns:
            Dict: Dicionário com as features extraídas ou None em caso de erro
        """
        folder_path = Path(folder_path)
        folder_name = folder_path.name
        output_file_path = RESPONSES_DIR / f"{folder_name}.json"

        try:
            content_parts = self._load_images_with_names(folder_path)
            if len(content_parts) <= 1:
                print(f"⚠️ Sem imagens válidas em {folder_name}")
                return None

            response = self.model.generate_content(content_parts)

            try:
                cleaned_text = self._extract_clean_json(response.text)
                response_json = json.loads(cleaned_text)
            except json.JSONDecodeError:
                print(f"❌ JSON inválido retornado por {folder_name}")
                response_json = {
                    "error": "Invalid JSON from model",
                    "raw_response": response.text
                }

            # Salva o resultado
            os.makedirs(RESPONSES_DIR, exist_ok=True)
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(response_json, f, indent=2, ensure_ascii=False)

            print(f"✅ JSON salvo em {output_file_path}")
            return response_json

        except Exception as e:
            error_info = {"error": str(e)}
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(error_info, f, indent=2, ensure_ascii=False)
            print(f"❌ Erro ao processar {folder_name}: {e}")
            return None

    def extract_features_in_memory(self, folder_path: Union[str, Path]) -> Optional[Dict]:
        """
        Extrai features de todas as imagens em uma pasta usando o Gemini, mantendo em memória sem salvar.
        
        Args:
            folder_path: Caminho para a pasta contendo as imagens JPG
            
        Returns:
            Dict: Dicionário com as features extraídas ou None em caso de erro
        """
        start_total = time.time()
        folder_path = Path(folder_path)
        folder_name = folder_path.name
        logger.info(f"[TIMER]     Starting feature extraction for {folder_name}")

        try:
            start_load = time.time()
            content_parts = self._load_images_with_names(folder_path)
            elapsed_load = time.time() - start_load
            logger.info(f"[TIMER]       Load images: {elapsed_load:.3f}s")
            
            if len(content_parts) <= 1:
                print(f"⚠️ Sem imagens válidas em {folder_name}")
                return None

            start_api = time.time()
            logger.info(f"[TIMER]       Iniciando chamada Gemini API com {len(content_parts)-1} imagens...")
            
            # Medir tempo de preparação do request
            start_prepare = time.time()
            # content_parts já contém: [prompt, "filename:", img, "filename:", img, ...]
            num_images = (len(content_parts) - 1) // 2
            elapsed_prepare = time.time() - start_prepare
            logger.info(f"[TIMER]         Preparação do request: {elapsed_prepare:.3f}s ({num_images} imagens)")
            
            # Chamada real ao Gemini (rede + processamento no servidor)
            start_call = time.time()
            response = self.model.generate_content(content_parts)
            elapsed_call = time.time() - start_call
            
            # Processar resposta
            start_response_processing = time.time()
            response_text = response.text
            prompt_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
            response_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
            elapsed_response_processing = time.time() - start_response_processing
            
            elapsed_api = time.time() - start_api
            
            logger.info(f"[TIMER]         Chamada Gemini (rede + servidor): {elapsed_call:.3f}s")
            logger.info(f"[TIMER]         Processar resposta: {elapsed_response_processing:.3f}s")
            logger.info(f"[TIMER]         Tokens: {prompt_tokens} prompt + {response_tokens} response = {prompt_tokens + response_tokens} total")
            logger.info(f"[TIMER]       TOTAL Gemini API call: {elapsed_api:.3f}s")
            print(response)

            start_parse = time.time()
            try:
                start_extract_text = time.time()
                cleaned_text = self._extract_clean_json(response_text)
                elapsed_extract_text = time.time() - start_extract_text
                
                start_json_parse = time.time()
                response_json = json.loads(cleaned_text)
                elapsed_json_parse = time.time() - start_json_parse
                
                elapsed_parse = time.time() - start_parse
                logger.info(f"[TIMER]       Parse - Extract clean JSON: {elapsed_extract_text:.3f}s, JSON loads: {elapsed_json_parse:.3f}s, Total: {elapsed_parse:.3f}s")
            except json.JSONDecodeError:
                print(f"❌ JSON inválido retornado por {folder_name}")
                response_json = {
                    "error": "Invalid JSON from model",
                    "raw_response": response.text
                }

            elapsed_total = time.time() - start_total
            logger.info(f"[TIMER]     TOTAL feature extraction: {elapsed_total:.3f}s")
            print(f"✅ Features extraídas para {folder_name} (em memória)")
            return response_json

        except Exception as e:
            print(f"❌ Erro ao processar {folder_name}: {e}")
            logger.error(f"[TIMER] ERROR in feature extraction: {str(e)}")
            return None


    def process_all_folders(self) -> None:
        """
        Processa todas as pastas de imagens no diretório base.
        """
        for folder in Path(IMAGES_DIR).iterdir():
            if folder.is_dir():
                output_file = RESPONSES_DIR / f"{folder.name}.json"
                if output_file.exists():
                    print(f"⏩ Pulando {folder.name}, já existe {output_file}")
                    continue
                self.extract_features(folder)