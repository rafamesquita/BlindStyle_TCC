import base64
import json
import time
import logging
from pathlib import Path
from typing import List, Dict
from functools import lru_cache
from sqlalchemy.orm import Session

from src.schemas.sugestion import SugestionResponse, OutfitDisplay, Pieces
from src.repositories.suggestion_repository import SuggestionRepository
from src.utils.image_utils import compress_image_to_jpeg
from modules.vector_db import VectorDB
from modules.model_input import ModelInputBuilder
from modules.pytorch_model import ModelPredictor
from modules.config import FILTERED_DIR, IMAGES_DIR

logger = logging.getLogger(__name__)

# TODO: DESCOMENTAR CACHE LRU PARA GANHO DE PERFORMANCE
# Benefício esperado: 2ª requisição ~10-50ms (vs ~75ms atuais)
# Trade-off: ~100-200MB RAM para cache
# OTIMIZAÇÃO: Cache LRU (Least Recently Used)
# Comentado temporariamente para benchmark sem cache
# @lru_cache(maxsize=1000)
# def load_outfit_json(outfit_id: str) -> Dict:
#     """Cache LRU para carregar JSONs de outfits"""
#     outfit_features_path = Path(f"../filtered_outfits/{outfit_id}.json")
#     if not outfit_features_path.exists():
#         return {}
#     with open(outfit_features_path, "r") as f:
#         return json.load(f)

# @lru_cache(maxsize=2000)
# def load_image_base64(outfit_id: str, piece_name: str) -> str:
#     """Cache LRU para carregar e codificar imagens em base64"""
#     image_path = Path(f"../archive/images/{outfit_id}/{piece_name}")
#     if not image_path.exists():
#         return ""
#     with open(image_path, "rb") as img_file:
#         return base64.b64encode(img_file.read()).decode('utf-8')

class SuggestionAppService:
    def __init__(
        self, 
        db: Session,
        vector_db: VectorDB,
        model_predictor: ModelPredictor,
        model_input_builder: ModelInputBuilder
    ):
        self.db = db
        self.vector_db = vector_db
        self.model_predictor = model_predictor
        self.model_input_builder = model_input_builder
        self.suggestion_repository = SuggestionRepository(db)

    async def generate_suggestion(self, item_id: int, user_id: int) -> SugestionResponse:
        start_total = time.time()
        logger.info(f"[TIMER] Starting generate_suggestion for item_id={item_id}, user_id={user_id}")
        
        collection_name = f"user_{str(user_id)}_pieces"
        
        # Get target item from database to get category
        start_get_item = time.time()
        from src.repositories.item_repository import ItemRepository
        item_repo = ItemRepository(self.db)
        target_item = item_repo.get_by_id(item_id, user_id)
        if not target_item:
            raise ValueError(f"Item {item_id} not found for user {user_id}")
        target_category = target_item.category
        elapsed_get_item = time.time() - start_get_item
        logger.info(f"[TIMER] Get target item (category={target_category}): {elapsed_get_item:.3f}s")

        # Get target embedding
        start_get_embedding = time.time()
        embedding_data = self.vector_db.get_by_id(collection_name, str(item_id))
        if embedding_data is None:
            raise ValueError(f"Embedding not found for item_id {item_id} in user's collection {collection_name}")
        embedding = embedding_data["embedding"]
        elapsed_get_embedding = time.time() - start_get_embedding
        logger.info(f"[TIMER] Get target embedding: {elapsed_get_embedding:.3f}s")

        # Search similar items
        start_search = time.time()
        # TODO: REFATORAR QUANDO CHROMADB FOR REPOPULADO COM METADATA DE CATEGORIA
        # Atualmente fazemos filtragem em Python lendo JSONs (overhead ~26ms)
        # Implementação ideal quando metadata existir:
        # similar_results = self.vector_db.search_similar(
        #     "pieces", 
        #     embedding, 
        #     n_results=10,
        #     filter_dict={"category": target_category}
        # )
        similar_results = self.vector_db.search_similar("pieces", embedding, n_results=10)
        similar_ids = similar_results['ids'][0]
        elapsed_search = time.time() - start_search
        logger.info(f"[TIMER] Search similar items: {elapsed_search:.3f}s")
        
        # WORKAROUND: Filter similar items by category using filtered_outfits JSONs
        # TODO: REMOVER quando ChromaDB tiver metadata de categoria
        start_filter_category = time.time()
        filtered_similar_ids = []
        for sid in similar_ids:
            outfit_id, piece_filename = sid.split('/')
            outfit_json_path = FILTERED_DIR / f"{outfit_id}.json"
            
            try:
                with open(outfit_json_path, "r") as f:
                    outfit_data = json.load(f)
                    piece_data = outfit_data.get(piece_filename, {})
                    piece_category = piece_data.get("category", "")
                    
                    # Only include if same category as target
                    if piece_category == target_category:
                        filtered_similar_ids.append(sid)
            except Exception as e:
                logger.warning(f"Could not check category for {sid}: {e}")
                continue
        
        elapsed_filter_category = time.time() - start_filter_category
        logger.info(f"[TIMER] Filter by category ({len(similar_ids)} -> {len(filtered_similar_ids)}): {elapsed_filter_category:.3f}s")
        
        # Use filtered IDs for rest of processing
        similar_ids = filtered_similar_ids
        
        # Get unique outfits
        start_get_outfits = time.time()
        unique_outfits = set()
        for sid in similar_ids:
            outfit_id = sid.split('/')[0]
            unique_outfits.add(outfit_id)
        
        outfit_ids_list = list(unique_outfits)
        outfits_dict = self.vector_db.get_pieces_by_outfits_batch("pieces", outfit_ids_list)
        
        elapsed_get_outfits = time.time() - start_get_outfits
        logger.info(f"[TIMER] Get {len(unique_outfits)} unique outfits (BATCH): {elapsed_get_outfits:.3f}s")
        
        # Remover do dicionário de outfits as peças similares que vieram da busca
        start_filter = time.time()
        similar_piece_ids = set(similar_ids)
        
        for outfit_id in outfits_dict.keys():
            # Filtra peças, removendo as que estão nos resultados de similaridade
            original_pieces = outfits_dict[outfit_id]
            filtered_pieces = [
                piece for piece in original_pieces 
                if piece['piece_id'] not in similar_piece_ids
            ]
            outfits_dict[outfit_id] = filtered_pieces
        elapsed_filter = time.time() - start_filter
        logger.info(f"[TIMER] Filter similar pieces: {elapsed_filter:.3f}s")
        
        # Gera inputs em batch para todos os outfits
        start_build_inputs = time.time()
        batch_inputs = self.model_input_builder.build_batch_inputs(
            new_piece_embedding=embedding,
            outfits_dict=outfits_dict
        )
        elapsed_build_inputs = time.time() - start_build_inputs
        logger.info(f"[TIMER] Build model inputs: {elapsed_build_inputs:.3f}s")

        # Usar modelo injetado (já carregado)
        # Avaliar cada outfit com o modelo e filtrar top 3
        # Predição em batch para todos os outfits
        start_predict = time.time()
        all_scores = self.model_predictor.predict_batch(batch_inputs)
        elapsed_predict = time.time() - start_predict
        logger.info(f"[TIMER] Model prediction: {elapsed_predict:.3f}s for {len(batch_inputs)} outfits")
        
        # Filtra top 3 outfits com score >= 0.96 (threshold ótimo da ROC curve)
        start_top3 = time.time()
        top_3_outfits = self.model_predictor.get_top_k_outfits(
            scores=all_scores,
            k=3,
            min_threshold=0.96
        )
        elapsed_top3 = time.time() - start_top3
        logger.info(f"[TIMER] Get top 3 outfits: {elapsed_top3:.3f}s")

        # Persistir sugestão no banco de dados
        # Converte top 3 outfits para formato CSV com paths das imagens
        start_persist = time.time()
        outfit_csvs = []
        for outfit_id, score in top_3_outfits.items():
            # Busca as peças do outfit (sem a nova peça adicionada)
            outfit_pieces = outfits_dict.get(outfit_id, [])
            
            # Gera CSV com paths: archive\images\outfit_id\piece_name
            piece_paths = [
                f"archive\\images\\{outfit_id}\\{piece['piece_id'].split('/')[-1]}"
                for piece in outfit_pieces
            ]
            outfit_csvs.append(",".join(piece_paths))
        
        # Preenche com None se não houver 3 sugestões
        while len(outfit_csvs) < 3:
            outfit_csvs.append(None)
        
        # Verifica se já existe uma sugestão para este usuário e item, e deleta se existir
        existing_suggestion = self.suggestion_repository.get_by_user_and_item(user_id, item_id)
        if existing_suggestion:
            self.suggestion_repository.delete(existing_suggestion.id)
        
        # Salva no banco
        suggestion_record = self.suggestion_repository.create(
            user_id=user_id,
            item_id=item_id,
            outfit1=outfit_csvs[0],
            outfit2=outfit_csvs[1],
            outfit3=outfit_csvs[2]
        )
        elapsed_persist = time.time() - start_persist
        logger.info(f"[TIMER] Persist to database: {elapsed_persist:.3f}s")

        # Montar SuggestionResponse com base64 e descrições
        start_build_response = time.time()
        outfits_display = []
        
        for outfit_id, score in top_3_outfits.items():
            start_outfit = time.time()
            
            # Carrega features do outfit do arquivo filtered_outfits (SEM CACHE)
            start_load_json = time.time()
            outfit_features_path = FILTERED_DIR / f"{outfit_id}.json"
            
            if not outfit_features_path.exists():
                logger.warning(f"[TIMER]   Outfit JSON {outfit_id} not found, skipping")
                continue
            
            with open(outfit_features_path, "r") as f:
                outfit_features = json.load(f)
            elapsed_load_json = time.time() - start_load_json
            
            logger.info(f"[TIMER]   Load outfit JSON {outfit_id}: {elapsed_load_json:.3f}s")
            
            # Busca peças do outfit
            outfit_pieces = outfits_dict.get(outfit_id, [])
            pieces_list: List[Pieces] = []
            
            start_pieces = time.time()
            for piece in outfit_pieces:
                piece_name = piece['piece_id'].split('/')[-1]
                image_path = IMAGES_DIR / outfit_id / piece_name
                
                # Converte e COMPRIME imagem para base64
                start_base64 = time.time()
                image_base64 = ""
                if image_path.exists():
                    try:
                        with open(image_path, "rb") as img_file:
                            image_data = img_file.read()
                            # Comprimir para JPEG quality=75 (redução ~50-60%)
                            image_base64 = compress_image_to_jpeg(image_data, quality=75, return_base64=True)
                            logger.debug(f"Compressed image {piece_name}: {len(image_base64)} chars")
                    except Exception as e:
                        logger.error(f"Error compressing image {piece_name}: {e}")
                        # Fallback: retorna vazio mas não quebra o fluxo
                        image_base64 = ""
                else:
                    logger.warning(f"Image not found: {image_path}")
                elapsed_base64 = time.time() - start_base64
                
                # Gera descrição a partir das features
                start_description = time.time()
                piece_features = outfit_features.get(f"{piece_name}", {})
                description = self._generate_description_from_features(piece_features)
                elapsed_description = time.time() - start_description
                
                logger.info(f"[TIMER]     Piece {piece_name}: base64={elapsed_base64:.3f}s, description={elapsed_description:.3f}s")
                
                pieces_list.append(Pieces(
                    piece_id=piece['piece_id'],
                    image_base64=image_base64,
                    description=description
                ))
            elapsed_pieces = time.time() - start_pieces
            
            outfits_display.append(OutfitDisplay(outfit_id=outfit_id, pieces=pieces_list, probability=score))
            elapsed_outfit = time.time() - start_outfit
            logger.info(f"[TIMER]   Total outfit {outfit_id}: {elapsed_outfit:.3f}s ({len(pieces_list)} pieces)")
        
        # Preenche com None se não houver 3 sugestões
        while len(outfits_display) < 3:
            outfits_display.append(None)
        
        elapsed_build_response = time.time() - start_build_response
        logger.info(f"[TIMER] Build response with images: {elapsed_build_response:.3f}s")
        
        elapsed_total = time.time() - start_total
        logger.info(f"[TIMER] TOTAL generate_suggestion: {elapsed_total:.3f}s")
        logger.info(f"[TIMER] Breakdown - Embedding: {elapsed_get_embedding:.3f}s | Search: {elapsed_search:.3f}s | Get outfits: {elapsed_get_outfits:.3f}s | Filter: {elapsed_filter:.3f}s | Build inputs: {elapsed_build_inputs:.3f}s | Predict: {elapsed_predict:.3f}s | Top3: {elapsed_top3:.3f}s | Persist: {elapsed_persist:.3f}s | Response: {elapsed_build_response:.3f}s")
        
        return SugestionResponse(
            Outfit1=outfits_display[0],
            Outfit2=outfits_display[1],
            Outfit3=outfits_display[2]
        )
    
    def _generate_description_from_features(self, features: dict) -> str:
        """
        Gera descrição textual a partir das features da peça
        
        Args:
            features: Dicionário com category, item_type, primary_color, usage, texture, print_category
            
        Returns:
            str: Descrição textual da peça
        """
        if not features:
            return "Item de vestuário"
        
        parts = []
        
        # Cor e tipo
        color = features.get("primary_color", "")
        item_type = features.get("item_type", "")
        
        if color and item_type:
            parts.append(f"{color} {item_type}")
        elif item_type:
            parts.append(item_type)
        
        # Textura
        texture = features.get("texture", "")
        if texture and texture != "plain":
            parts.append(f"de {texture}")
        
        # Categoria de estampa
        print_cat = features.get("print_category", "")
        if print_cat and print_cat != "plain":
            parts.append(f"com estampa {print_cat}")
        
        # Uso
        usage = features.get("usage", "")
        if usage:
            parts.append(f"para uso {usage}")
        
        description = " ".join(parts) if parts else "Item de vestuário"
        
        # Capitaliza primeira letra
        return description[0].upper() + description[1:] if description else "Item"
