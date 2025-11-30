"""
Módulo para preparação de inputs para o modelo MCN (Multi-Correlation Network)

Este módulo é responsável por transformar embeddings de peças de roupa em inputs
adequados para o modelo de compatibilidade de outfit.
"""

import numpy as np
from typing import List, Dict, Tuple


class ModelInputBuilder:
    """
    Constrói inputs para o modelo MCN a partir de embeddings de peças
    """
    
    def __init__(self, max_items: int = 5, embedding_dim: int = 96):
        """
        Inicializa o construtor de inputs
        
        Args:
            max_items: Número máximo de peças por outfit (padrão: 5)
            embedding_dim: Dimensão dos embeddings (padrão: 96)
        """
        self.max_items = max_items
        self.embedding_dim = embedding_dim
    
    def build_input(
        self, 
        new_piece_embedding: np.ndarray,
        outfit_pieces: List[Dict]
    ) -> Tuple[np.ndarray, np.ndarray, int]:
        """
        Constrói input para o modelo adicionando uma nova peça a um outfit existente
        
        Args:
            new_piece_embedding: Embedding (96,) da nova peça a ser avaliada
            outfit_pieces: Lista de dicts com 'embedding' das peças do outfit original
            
        Returns:
            Tuple contendo:
                - embeddings: Array (max_items, 96) com padding
                - mask: Array (max_items,) boolean indicando peças válidas (True) e padding (False)
                - num_items: Número real de itens (incluindo a nova peça)
                
        Raises:
            ValueError: Se o número de peças exceder max_items
        """
        # Coleta embeddings das peças do outfit original
        outfit_embeddings = [
            np.array(piece['embedding'], dtype=np.float32) 
            for piece in outfit_pieces
        ]
        
        # Adiciona o embedding da nova peça
        all_embeddings = outfit_embeddings + [np.array(new_piece_embedding, dtype=np.float32)]
        
        num_items = len(all_embeddings)
        
        # Validação estrita de máximo de itens - não trunca, lança erro
        if num_items > self.max_items:
            raise ValueError(
                f"Número de peças ({num_items}) excede o máximo permitido ({self.max_items}). "
                f"Outfit original tem {len(outfit_embeddings)} peças + 1 nova peça."
            )
        
        # Cria array com padding (consistente com models/dataset.py linha 109)
        embeddings = np.zeros((self.max_items, self.embedding_dim), dtype=np.float32)
        
        # Cria máscara boolean (consistente com models/dataset.py linha 113-114)
        mask = np.zeros(self.max_items, dtype=bool)
        mask[:num_items] = True
        
        # Preenche com embeddings reais
        for i, emb in enumerate(all_embeddings):
            embeddings[i] = emb
        
        return embeddings, mask, num_items
    
    def build_batch_inputs(
        self,
        new_piece_embedding: np.ndarray,
        outfits_dict: Dict[str, List[Dict]]
    ) -> Dict[str, Tuple[np.ndarray, np.ndarray, int]]:
        """
        Constrói inputs em batch para múltiplos outfits
        
        Args:
            new_piece_embedding: Embedding da nova peça
            outfits_dict: Dicionário {outfit_id: [pieces]}
            
        Returns:
            Dict {outfit_id: (embeddings, mask, num_items)}
            
        Raises:
            ValueError: Se algum outfit exceder max_items
        """
        batch_inputs = {}
        
        for outfit_id, pieces in outfits_dict.items():
            # Pula outfits vazios (todas as peças foram similares e removidas)
            if not pieces:
                continue
            
            try:
                embeddings, mask, num_items = self.build_input(
                    new_piece_embedding,
                    pieces
                )
                
                batch_inputs[outfit_id] = (embeddings, mask, num_items)
                
            except ValueError as e:
                # Re-lança erro com contexto do outfit
                raise ValueError(f"Erro ao processar outfit '{outfit_id}': {str(e)}")
        
        return batch_inputs


def generate_description_from_features(outfit_features: Dict[str, Dict]) -> str:
    """
    Gera descrição textual de um outfit baseado nas features das peças
    
    Args:
        outfit_features: Dict {piece_name: {category, item_type, color, ...}}
        
    Returns:
        String com descrição do outfit
    """
    if not outfit_features:
        return "Outfit sem peças disponíveis"
    
    descriptions = []
    
    for piece_name, features in outfit_features.items():
        # Extrai features principais
        item_type = features.get('item_type', 'item')
        color = features.get('primary_color', '')
        texture = features.get('texture', '')
        usage = features.get('usage', '')
        
        # Monta descrição da peça
        desc_parts = []
        if color:
            desc_parts.append(color)
        if texture:
            desc_parts.append(texture)
        desc_parts.append(item_type)
        
        piece_desc = ' '.join(desc_parts)
        descriptions.append(piece_desc.capitalize())
    
    # Junta todas as descrições
    if len(descriptions) == 1:
        return descriptions[0]
    elif len(descriptions) == 2:
        return f"{descriptions[0]} com {descriptions[1]}"
    else:
        return ', '.join(descriptions[:-1]) + f" e {descriptions[-1]}"
