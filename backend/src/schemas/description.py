from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class ItemCategory(str, Enum):
  TOPS = "tops"
  BOTTOMS = "bottoms"
  SHOES = "shoes"
  OTHERS = "others"

class ItemUsage(str, Enum):
  CASUAL = "casual"
  FORMAL = "formal"
  BUSINESS = "business"
  SPORTSWEAR = "sportswear"
  SLEEPWEAR = "sleepwear"
  OUTERWEAR = "outerwear"
  PARTY = "party"
  WORKWEAR = "workwear"

class ItemTexture(str, Enum):
  COTTON = "cotton"
  DENIM = "denim"
  LEATHER = "leather"
  POLYESTER = "polyester"
  WOOL = "wool"
  SILK = "silk"
  LINEN = "linen"
  KNIT = "knit"
  SUEDE = "suede"
  NYLON = "nylon"
  FLEECE = "fleece"
  VELVET = "velvet"
  MESH = "mesh"
  OTHERS = "others"

class ItemPrint(str, Enum):
  STRIPED = "striped"
  ANIMAL = "animal"
  FLORAL = "floral"
  PLAID = "plaid"
  PLAIN = "plain"
  ABSTRACT = "abstract"
  LOGO = "logo"
  GRAPHIC = "graphic"

class ClothingFeatures(BaseModel):
  category: str
  item_type: str
  primary_color: str
  usage: str
  texture: str
  print_category: str

class FeatureExtractionRequest(BaseModel):
  image_base64: Optional[str] = Field(None, description="Imagem em base64")
  image_url: Optional[str] = Field(None, description="URL da imagem")

#TODO check if features should be optional later
class FeatureExtractionResponse(BaseModel):
  success: bool
  description: str
  features: Optional[ClothingFeatures] = None