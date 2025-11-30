"""
MCN (Multi-Correlation Network) Model for Outfit Compatibility

This module implements an adepted version of the MCN architecture based on Wang et al. (2019):
"Outfit Compatibility Prediction and Diagnosis with Multi-Layered Comparison Network"

Architecture:
1. Feature Projection: Projects 96-D embeddings to 1000-D space
2. Pairwise Comparisons: Computes similarity between all item pairs with learnable masks
3. Compatibility Predictor: MLP that predicts final compatibility score
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


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

    print(f"\n🔧 MCN Model Created:")
    print(f"  Input dimension: {model.embed_input_size}")
    print(f"  Projection dimension: {model.embed_proj_size}")
    print(f"  Max items: {model.max_items}")
    print(f"  Number of pairs: {model.num_pairs}")
    print(f"  Total parameters: {model.get_num_parameters():,}")
    print(f"  Trainable parameters: {model.get_trainable_parameters():,}")
    print(f"  Dropout rate: {model.dropout}")

    return model


if __name__ == "__main__":
    """Test the model implementation"""
    print("🧪 Testing OutfitCompatibilityModel...\n")
    
    # Create dummy data
    batch_size = 4
    max_items = 5
    embed_size = 96
    
    # Simulate batch with different outfit sizes
    embeddings = torch.randn(batch_size, max_items, embed_size)
    
    # Create masks (simulate outfits with 2, 3, 4, 5 items)
    mask = torch.zeros(batch_size, max_items, dtype=torch.bool)
    mask[0, :2] = True  # 2 items
    mask[1, :3] = True  # 3 items
    mask[2, :4] = True  # 4 items
    mask[3, :5] = True  # 5 items
    
    print(f"Input shapes:")
    print(f"  Embeddings: {embeddings.shape}")
    print(f"  Mask: {mask.shape}")
    print(f"  Mask values:\n{mask}")
    
    # Create model
    config = {
        'embed_input_size': 96,
        'embed_proj_size': 1000,
        'max_items': 5,
        'dropout': 0.3
    }
    
    model = create_model(config)
    
    # Forward pass
    print(f"\n🔄 Running forward pass...")
    model.eval()
    with torch.no_grad():
        outputs = model(embeddings, mask)
    
    print(f"\nOutput shape: {outputs.shape}")
    print(f"Output values: {outputs}")
    print(f"Output range: [{outputs.min():.4f}, {outputs.max():.4f}]")
    
    # Test gradients
    print(f"\n🔄 Testing gradient flow...")
    model.train()
    outputs = model(embeddings, mask)
    loss = outputs.mean()
    loss.backward()
    
    # Check if gradients exist
    has_grads = all(p.grad is not None for p in model.parameters() if p.requires_grad)
    print(f"  All parameters have gradients: {has_grads}")
    
    print("\n✅ Model test passed!")
