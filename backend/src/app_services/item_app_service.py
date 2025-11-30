from typing import Optional, Dict
from src.services.item_service import ItemService
from src.schemas.item import (
    ItemCreate,
    ItemUpdate,
    Item as ItemSchema,
    ItemStatus,
    ItemList,
    ItemStatusUpdate
)

class ItemAppService:
    def __init__(self, item_service: ItemService):
        self.item_service = item_service

    def create_item(self, user_id: int, item_data: ItemCreate) -> ItemSchema:
        item = self.item_service.create_item(user_id, item_data)
        return ItemSchema.model_validate(item)

    def get_item(self, item_id: int, user_id: int, allow_others: bool = False) -> ItemSchema:
        item = self.item_service.get_item(item_id, user_id, allow_others)
        return ItemSchema.model_validate(item)

    def list_user_items(self, user_id: int, page: int = 1, size: int = 10, status: Optional[ItemStatus] = ItemStatus.ACTIVE, category: Optional[str] = None) -> ItemList:
        items, total = self.item_service.list_user_items(user_id=user_id, page=page, size=size, status=status, category=category)
        return ItemList(items=[ItemSchema.model_validate(item) for item in items], total=total, page=page, size=size)

    def update_item(self, item_id: int, user_id: int, item_data: ItemUpdate) -> ItemSchema:
        item = self.item_service.update_item(item_id, user_id, item_data)
        return ItemSchema.model_validate(item)

    def update_item_status(self, item_id: int, user_id: int, status_update: ItemStatusUpdate) -> ItemSchema:
        item = self.item_service.update_item_status(item_id, user_id, status_update.status)
        return ItemSchema.model_validate(item)

    def delete_item(self, item_id: int, user_id: int, permanent: bool = False) -> Dict[str, str]:
        return self.item_service.delete_item(item_id, user_id, permanent)