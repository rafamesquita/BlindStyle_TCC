"""
Utility module for formatting clothing feature descriptions.

This module provides functions to generate human-readable descriptions
from structured clothing feature data.
"""

from typing import Dict, Any


def generate_description_from_features(features: Dict[str, Any]) -> str:
    """
    Generate a natural language description from clothing features.
    
    Args:
        features: Dictionary containing clothing features (category, item_type, 
                 primary_color, texture, print_category, usage)
    
    Returns:
        str: Human-readable description of the clothing item
    
    Examples:
        >>> features = {
        ...     "category": "camisa",
        ...     "item_type": "social",
        ...     "primary_color": "azul",
        ...     "texture": "lisa",
        ...     "usage": "trabalho"
        ... }
        >>> generate_description_from_features(features)
        'Um camisa, do tipo social, de cor azul, com textura lisa, e recomendado para uso de trabalho'
    """
    parts = []

    if category := features.get("category"):
        parts.append(f"Um {category}")

    if item_type := features.get("item_type"):
        parts.append(f"do tipo {item_type}")

    if color := features.get("primary_color"):
        parts.append(f"de cor {color}")

    if texture := features.get("texture"):
        parts.append(f"com textura {texture}")

    if print_category := features.get("print_category"):
        parts.append(f"estampa {print_category}")

    if usage := features.get("usage"):
        parts.append(f"e recomendado para uso de {usage}")

    if not parts:
        return "Nenhuma informação disponível sobre o item."

    if len(parts) > 1 and parts[-1].startswith("e "):
        return ", ".join(parts[:-1]) + ", " + parts[-1]
    else:
        return ", ".join(parts)
