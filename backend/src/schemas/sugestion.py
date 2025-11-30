from pydantic import BaseModel, Field
from typing import Optional, List


class Pieces(BaseModel):
    piece_id: str
    image_base64: str
    description: str
    
class OutfitDisplay(BaseModel):
    outfit_id: str
    pieces: List[Pieces]
    probability: float


class SugestionResponse(BaseModel):
    """Schema base para itens"""
    Outfit1: Optional[OutfitDisplay] = Field(..., description="Outfit 1 recomendado")
    Outfit2: Optional[OutfitDisplay] = Field(..., description="Outfit 2 recomendado")
    Outfit3: Optional[OutfitDisplay] = Field(..., description="Outfit 3 recomendado")