import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
from modules.config import (
    FILTERED_DIR,
    ATTRIBUTES,
    ATTR_DIM,
)
from .vector_db import VectorDB

class EmbeddingGenerator:
    def __init__(self, vector_db: Optional[VectorDB] = None):
        """Inicializa o gerador de embeddings"""
        self.vector_db = vector_db
    
    def _hash_embedding(self, text: str, dim: int = 16) -> np.ndarray:
        """
        Gera embedding determinístico baseado em hash MD5
        
        Args:
            text: Texto para gerar embedding (formato: "atributo:valor")
            dim: Dimensão do embedding (default: 16)
        
        Returns:
            np.ndarray: Embedding normalizado em float32
        """
        # Create a deterministic seed from md5 hash
        md5 = hashlib.md5(text.encode("utf-8")).hexdigest()
        seed = int(md5[:8], 16)  # use first 8 hex digits as integer

        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(dim)
        normalized = vec / np.linalg.norm(vec)
        # Garantir float32 para consistência
        return normalized.astype(np.float32)
    
    

    def _generate_piece_embedding(self, piece_data: Dict) -> np.ndarray:
        """
        Gera embedding para uma peça de roupa
        
        CORREÇÃO: Todos os 6 atributos sempre geram embeddings únicos
        - category, item_type, primary_color, usage, texture, print_category
        - Cada um gera um vetor de dimensão ATTR_DIM (16)
        - Total: 6 × 16 = 96 dimensões
        
        Args:
            piece_data: Dicionário com atributos da peça
        
        Returns:
            np.ndarray: Embedding concatenado (96,) em float32
        """
        embeddings = []
        
        # Processa cada atributo definido
        for attr in ATTRIBUTES:
            value = piece_data.get(attr, "UNK")
            encoding = self._hash_embedding(f"{attr}:{value}", ATTR_DIM)
            embeddings.append(encoding)
        
        # Concatena todos os embeddings de atributos e garante float32
        return np.concatenate(embeddings).astype(np.float32)

    def _process_outfit(self, outfit_data: Dict, file_name: str) -> Tuple[List[np.ndarray], List[str]]:
        """Processa um outfit gerando embeddings e metadados para cada peça"""
        embeddings = []
        ids = []
        outfit_name = file_name.replace(".json", "")
        
        for piece_id, piece_data in outfit_data.items():
            try:
                # Gera embedding da peça
                piece_embedding = self._generate_piece_embedding(piece_data)
                embeddings.append(piece_embedding)
                ids.append(f"{outfit_name}/{piece_id}")
                
            except Exception as e:
                print(f"❌ Erro ao processar peça {piece_id} do outfit {file_name}: {e}")
                continue
                
        return embeddings, ids

    def process_and_store(self, collection_name: str, limit: Optional[int] = None) -> List[str]:
        """
        Processa outfits filtrados e armazena no banco vetorial
        
        Args:
            collection_name: Nome da coleção onde salvar
            limit: Número máximo de arquivos a processar
        """
        processed_files = []
        db = self.vector_db or VectorDB()
        
        for count, file_path in enumerate(Path(FILTERED_DIR).glob("*.json")):
            if limit is not None and count >= limit:
                break
                
            try:
                # Carrega dados do outfit
                with open(file_path, "r", encoding="utf-8") as f:
                    outfit_data = json.load(f)
                
                # Processa outfit
                embeddings, ids = self._process_outfit(outfit_data, file_path.name)
                
                if embeddings and ids: 
                    # Adiciona ao banco vetorial
                    db.add_items(
                        collection_name=collection_name,
                        embeddings=[e.tolist() for e in embeddings],
                        ids=ids
                    )
                    
                    processed_files.append(file_path.name)
                    print(f"✅ Outfit {file_path.name} adicionado à coleção {collection_name}")
                
            except Exception as e:
                print(f"❌ Erro ao processar {file_path.name}: {e}")
                continue
        
        return processed_files