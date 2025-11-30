from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ItemStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"

class ItemBase(BaseModel):
    """Schema base para itens"""
    name: str = Field(..., description="Nome do item")
    description: Optional[str] = Field(None, description="Descrição detalhada do item")
    category: str = Field(..., description="Categoria geral do item (ex: roupa, acessório)")
    item_type: str = Field(..., description="Tipo específico do item (ex: blusa, calça jeans)")
    primary_color: str = Field(..., description="Cor primária do item")
    usage: str = Field(..., description="Uso pretendido do item (ex: casual, formal)")
    texture: str = Field(..., description="Textura do tecido ou material")
    print_category: str = Field(..., description="Categoria de estampa ou padrão (ex: liso, estampado)")
    image_url: str = Field(..., description="URL da imagem do item")
    ownership: Optional[bool] = Field(True, description="Indica se o item pertence ao usuário")

class ItemCreate(ItemBase):
    """Schema para criação de item"""
    pass

class ItemUpdate(BaseModel):
    """Schema para atualização de item"""
    name: Optional[str] = Field(None, description="Novo nome do item")
    description: Optional[str] = Field(None, description="Nova descrição do item")
    category: Optional[str] = Field(None, description="Nova categoria do item")
    color: Optional[str] = Field(None, description="Nova cor do item")
    image_url: Optional[str] = Field(None, description="Nova URL da imagem")
    ownership: Optional[bool] = Field(None, description="Nova indicação de propriedade do item")

class ItemStatusUpdate(BaseModel):
    """Schema para atualização de status de item"""
    status: ItemStatus = Field(..., description="Novo status do item")

class ClothingItemUpdateSchema(BaseModel):
    status: ItemStatus = Field(ItemStatus.ACTIVE, description="Status do item")

class ClothingItemSchema(ItemBase):
    """Schema compatível com versão anterior"""
    status: ItemStatus = Field(ItemStatus.ACTIVE, description="Status do item")
    
    class Config:
        from_attributes = True

class CompleteClothingItemSchema(ItemBase):
    """Schema compatível com versão anterior para respostas completas"""
    id: int = Field(..., description="ID único do item")
    created_at: datetime = Field(..., description="Data de criação")
    status: ItemStatus = Field(ItemStatus.ACTIVE, description="Status do item")
    
    class Config:
        from_attributes = True

class Item(ItemBase):
    """Schema completo de item com dados adicionais"""
    id: int = Field(..., description="ID único do item")
    user_id: int = Field(..., description="ID do usuário dono do item")
    status: ItemStatus = Field(..., description="Status atual do item")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data da última atualização")
    
    class Config:
        from_attributes = True

class ItemList(BaseModel):
    """Schema para lista paginada de itens"""
    items: List[Item] = Field(..., description="Lista de itens")
    total: int = Field(..., description="Total de itens")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Itens por página")