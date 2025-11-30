"""
Módulo PyTorch Model para Compatibilidade de Outfits

Contém a arquitetura MCN (Multi-Correlation Network) e funções de predição
para inferência em produção.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional


class OutfitCompatibilityModel(nn.Module):
    """
    MCN model for outfit compatibility prediction
    
    Handles variable-length outfits (2-5 items) using padding and masking.
    """

    def __init__(
        self,
        embed_input_size: int = 96,
        embed_proj_size: int = 1000,
        max_items: int = 5,
        dropout: float = 0.3
    ):
        """
        Initialize MCN model
        
        Args:
            embed_input_size: Input embedding dimension (96 for our dataset)
            embed_proj_size: Projection dimension (1000 as per paper)
            max_items: Maximum number of items in an outfit
            dropout: Dropout rate for regularization
        """
        super(OutfitCompatibilityModel, self).__init__()

        self.embed_input_size = embed_input_size
        self.embed_proj_size = embed_proj_size
        self.max_items = max_items
        self.dropout = dropout

        # Number of pairwise comparisons for max_items
        # For 5 items: 5*6/2 = 15 pairs (including self-comparisons)
        self.num_pairs = (max_items * (max_items + 1)) // 2

        # 1. Feature Projection Layer
        # Projects embeddings from 96-D to 1000-D
        self.feature_proj = nn.Sequential(
            nn.Linear(embed_input_size, embed_proj_size),
            nn.BatchNorm1d(embed_proj_size),
            nn.ReLU(),
            nn.Dropout(dropout)
        )

        # 2. Learnable Masks for Pairwise Comparisons
        # One mask per pair to learn which features are important
        self.masks = nn.Embedding(self.num_pairs, embed_proj_size)
        
        # Initialize masks with small positive values
        nn.init.uniform_(self.masks.weight, 0, 0.1)

        # 3. Batch Normalization for Relations
        self.bn_relations = nn.BatchNorm1d(self.num_pairs)

        # 4. Compatibility Predictor (MLP)
        # Takes pairwise similarities and predicts compatibility
        self.predictor = nn.Sequential(
            nn.Linear(self.num_pairs, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid()  # Output probability [0, 1]
        )

        # Initialize predictor weights with Xavier
        self._initialize_predictor()

    def _initialize_predictor(self):
        """Initialize predictor layers with Xavier uniform"""
        for module in self.predictor.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)

    def forward(
        self,
        embeddings: torch.Tensor,
        mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Forward pass through the model
        
        Args:
            embeddings: (batch_size, max_items, embed_input_size) - outfit embeddings
            mask: (batch_size, max_items) - boolean mask for valid items
            
        Returns:
            compatibility_scores: (batch_size,) - compatibility scores in [0, 1]
        """
        batch_size = embeddings.shape[0]

        # 1. Project features to higher dimension
        # Reshape to apply batch norm correctly
        flat_embeddings = embeddings.reshape(-1, self.embed_input_size)  # (B*max_items, 96)
        projected = self.feature_proj(flat_embeddings)  # (B*max_items, 1000)
        features = projected.reshape(batch_size, self.max_items, self.embed_proj_size)

        # 2. Compute pairwise comparisons with learnable masks
        relations = []
        mask_weights = F.relu(self.masks.weight)  # (num_pairs, 1000) - ensure positive

        pair_idx = 0
        for i in range(self.max_items):
            for j in range(i, self.max_items):  # Upper triangular including diagonal
                # Check if both items are valid (not padding)
                pair_valid = mask[:, i] & mask[:, j]  # (batch_size,)

                # Apply learnable mask and normalize
                left = F.normalize(
                    mask_weights[pair_idx] * features[:, i],
                    dim=-1
                )  # (batch_size, 1000)

                right = F.normalize(
                    mask_weights[pair_idx] * features[:, j],
                    dim=-1
                )  # (batch_size, 1000)

                # Compute similarity (dot product)
                relation = (left * right).sum(dim=-1)  # (batch_size,)

                # Zero out invalid pairs
                relation = relation * pair_valid.float()

                relations.append(relation)
                pair_idx += 1

        # Stack all pairwise relations
        relations = torch.stack(relations, dim=1)  # (batch_size, num_pairs)

        # 3. Normalize relations
        relations = self.bn_relations(relations)

        # 4. Predict compatibility
        compatibility_scores = self.predictor(relations).squeeze(-1)  # (batch_size,)

        return compatibility_scores

    def get_num_parameters(self) -> int:
        """Return total number of parameters"""
        return sum(p.numel() for p in self.parameters())

    def get_trainable_parameters(self) -> int:
        """Return number of trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def create_model(config: dict) -> OutfitCompatibilityModel:
    """
    Factory function to create model from config
    
    Args:
        config: Dictionary with model configuration
        
    Returns:
        Initialized model
    """
    model = OutfitCompatibilityModel(
        embed_input_size=config.get('embed_input_size', 96),
        embed_proj_size=config.get('embed_proj_size', 1000),
        max_items=config.get('max_items', 5),
        dropout=config.get('dropout', 0.3)
    )

    return model


class ModelPredictor:
    """
    Classe para carregar e executar predições do modelo MCN
    """
    
    def __init__(
        self,
        checkpoint_path: str,
        device: Optional[str] = None,
        config: Optional[Dict] = None
    ):
        """
        Inicializa o preditor do modelo
        
        Args:
            checkpoint_path: Caminho relativo ao checkpoint do modelo (.pth)
            device: Device para predição ('cpu' ou 'cuda'). Se None, detecta automaticamente
            config: Configuração do modelo (se None, usa defaults)
        """
        # Path relativo a partir do módulo backend
        module_dir = Path(__file__).parent
        self.checkpoint_path = module_dir / checkpoint_path
        
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint não encontrado: {self.checkpoint_path}")
        
        # Detecta device automaticamente se não especificado
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        # Configuração padrão do modelo
        self.config = config or {
            'embed_input_size': 96,
            'embed_proj_size': 1000,
            'max_items': 5,
            'dropout': 0.3
        }
        
        # Carrega o modelo
        self.model = self._load_model()
        
    def _load_model(self) -> nn.Module:
        """
        Carrega o modelo do checkpoint
        
        Returns:
            Modelo carregado em modo de avaliação
        """
        # Cria arquitetura do modelo
        model = create_model(self.config)
        
        # Carrega pesos do checkpoint
        checkpoint = torch.load(
            self.checkpoint_path,
            map_location=self.device,
            weights_only=False
        )
        
        model.load_state_dict(checkpoint['model_state_dict'])
        
        # Move para device e modo de avaliação
        model.to(self.device)
        model.eval()
        
        print(f"✅ Modelo carregado de: {self.checkpoint_path.name}")
        print(f"  Device: {self.device}")
        print(f"  Época: {checkpoint.get('epoch', 'N/A')}")
        print(f"  AUC de validação: {checkpoint.get('best_val_auc', 'N/A'):.4f}")
        
        return model
    
    def predict_single(
        self,
        embeddings: np.ndarray,
        mask: np.ndarray
    ) -> float:
        """
        Executa predição para um único outfit
        
        Args:
            embeddings: Array (max_items, 96) com embeddings das peças
            mask: Array (max_items,) boolean indicando peças válidas
            
        Returns:
            Score de compatibilidade entre 0 e 1
        """
        # Converte para tensores PyTorch e adiciona dimensão de batch
        embeddings_tensor = torch.from_numpy(embeddings).unsqueeze(0).to(self.device)
        mask_tensor = torch.from_numpy(mask).unsqueeze(0).to(self.device)
        
        # Inferência
        with torch.no_grad():
            output = self.model(embeddings_tensor, mask_tensor)
        
        # Extrai score (remove dimensão de batch e converte para float)
        score = output.squeeze().item()
        
        return score
    
    def predict_batch(
        self,
        batch_inputs: Dict[str, Tuple[np.ndarray, np.ndarray, int]]
    ) -> Dict[str, float]:
        """
        Executa predição em batch para múltiplos outfits
        
        Args:
            batch_inputs: Dict {outfit_id: (embeddings, mask, num_items)}
            
        Returns:
            Dict {outfit_id: compatibility_score}
        """
        scores = {}
        
        for outfit_id, (embeddings, mask, num_items) in batch_inputs.items():
            score = self.predict_single(embeddings, mask)
            scores[outfit_id] = score
        
        return scores
    
    def get_top_k_outfits(
        self,
        scores: Dict[str, float],
        k: int = 3,
        min_threshold: float = 0.8
    ) -> Dict[str, float]:
        """
        Retorna os top-k outfits acima de um limiar mínimo
        
        Args:
            scores: Dict {outfit_id: score}
            k: Número de top outfits a retornar
            min_threshold: Score mínimo para considerar (default: 0.8)
            
        Returns:
            Dict {outfit_id: score} com no máximo k outfits acima do limiar,
            ordenados por score decrescente
        """
        # Filtra scores acima do limiar
        filtered_scores = {
            outfit_id: score
            for outfit_id, score in scores.items()
            if score >= min_threshold
        }
        
        # Ordena por score decrescente e pega top-k
        sorted_scores = dict(
            sorted(
                filtered_scores.items(),
                key=lambda item: item[1],
                reverse=True
            )[:10]
        )
        
        return sorted_scores


# Singleton para cache do modelo (evita recarregar a cada requisição)
_model_cache: Optional[ModelPredictor] = None


def get_model_predictor(
    checkpoint_path: str = "../checkpoints/best_model.pth",
    force_reload: bool = False
) -> ModelPredictor:
    """
    Obtém instância singleton do preditor do modelo
    
    Args:
        checkpoint_path: Caminho relativo para o checkpoint (default: ../checkpoints/best_model.pth)
        force_reload: Se True, força recarregamento do modelo
        
    Returns:
        Instância de ModelPredictor (cached)
    """
    global _model_cache
    
    if _model_cache is None or force_reload:
        _model_cache = ModelPredictor(checkpoint_path)
    
    return _model_cache
