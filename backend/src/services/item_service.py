import base64
from typing import List, Optional, Tuple, Dict
from src.repositories.item_repository import ItemRepository
from src.schemas.item import (
    ItemCreate, ItemUpdate, ItemStatus
)
from src.models.item import Item
from src.core.exceptions import ServiceError
from modules.embeddings import EmbeddingGenerator
from modules.vector_db import VectorDB


class ItemService:
    def __init__(
        self, 
        repository: ItemRepository,
        vector_db: VectorDB,
        embedding_generator: EmbeddingGenerator
    ):
        self.repository = repository
        self.vector_db = vector_db
        self.embedding_gen = embedding_generator

    def _encode_image_url(self, image_url: str) -> str:
        try:
            base64.b64decode(image_url)
            return image_url
        except:
            return image_url
            
    def _decode_image_base64(self, image_url: str) -> str:
        try:
            return base64.b64decode(image_url).decode('utf-8')
        except:
            return image_url

    def create_item(self, user_id: int, item_data: ItemCreate) -> Item:
        item_dict = item_data.model_dump()
        item_dict['image_url'] = self._decode_image_base64(item_dict['image_url'])

        item = self.repository.create(user_id, ItemCreate(**item_dict))
        collection_name = f"user_{user_id}_pieces"
        self.vector_db.get_or_create_collection(collection_name)

        piece_data = {
            "category": item_data.category,
            "item_type": item_data.item_type,  # Assuming item_type is in item
            "primary_color": item_data.primary_color,
            "usage": item_data.usage,  # Assuming usage is in item_data or default
            "texture": item_data.texture,  # Assuming texture is in item_data or default
            "print_category": item_data.print_category  # Assuming print_category is in item_data or default
        }
        
        # Generate embedding
        embedding = self.embedding_gen._generate_piece_embedding(piece_data)
        
        # Add to collection
        self.vector_db.add_item(
            collection_name=collection_name,
            embedding=embedding.tolist(),
            id=str(item.id),  # Use item ID as the unique key
        )
        
        return item

    def get_item(self, item_id: int, user_id: int, allow_others: bool = False) -> Item:
        item = self.repository.get_by_id(item_id, None if allow_others else user_id)
        if not item:
            raise ServiceError("Item não encontrado")
        if not allow_others and item.user_id != user_id:
            raise ServiceError("Sem permissão para acessar este item")
        return item

    def list_user_items(self, user_id: int, page: int = 1, size: int = 10, status: Optional[ItemStatus] = ItemStatus.ACTIVE, category: Optional[str] = None) -> Tuple[List[Item], int]:
        skip = (page - 1) * size
        return self.repository.list_items(user_id=user_id, skip=skip, limit=size, status=status, category=category)

    def update_item(self, item_id: int, user_id: int, item_data: ItemUpdate) -> Item:
        item = self.get_item(item_id, user_id)
        if not item:
            raise ServiceError("Item não encontrado")
            
        if item_data.image_url:
            item_data.image_url = self._decode_image_base64(item_data.image_url)

        #TODO UPDATE vector db with new embdedding
            
        updated_item = self.repository.update(item_id, user_id, item_data)
        if not updated_item:
            raise ServiceError("Falha ao atualizar o item")
        return updated_item

    def delete_item(self, item_id: int, user_id: int, permanent: bool = False) -> Dict[str, str]:
        item = self.get_item(item_id, user_id)
        if not item:
            raise ServiceError("Item não encontrado")
        
        #TODO DELETE in vector db
              
        if permanent:
            success = self.repository.hard_delete(item_id, user_id)
        else:
            success = self.repository.delete(item_id, user_id)
            
        if not success:
            raise ServiceError("Falha ao deletar o item")
        return {"message": "Item deletado com sucesso"}

    def update_item_status(self, item_id: int, user_id: int, status: ItemStatus) -> Item:
        """
        Atualiza apenas o status de um item

        Args:
            item_id: ID do item
            user_id: ID do usuário dono do item
            status: Novo status do item
            
        Returns:
            Item: Item atualizado (modelo SQLAlchemy)
            
        Raises:
            ServiceError: Se o item não for encontrado
        """
        updated_item = self.repository.update_status(item_id, user_id, status)
        if not updated_item:
            raise ServiceError("Item não encontrado")
        return updated_item