from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models.item import Item
from src.schemas.item import ItemCreate, ItemUpdate, ItemStatus

class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, item_data: ItemCreate) -> Item:
        db_item = Item(user_id=user_id, **item_data.model_dump())
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def get_by_id(self, item_id: int, user_id: Optional[int] = None) -> Optional[Item]:
        query = select(Item).where(Item.id == item_id)
        if user_id is not None:
            query = query.where(Item.user_id == user_id)
        return self.db.execute(query).scalar_one_or_none()

    def list_items(self, user_id: int, skip: int = 0, limit: int = 10, status: Optional[ItemStatus] = None, category: Optional[str] = None) -> Tuple[List[Item], int]:
        query = select(Item).where(Item.user_id == user_id)
        
        if status:
            query = query.where(Item.status == status)
        if category:
            query = query.where(Item.category == category)
            
        total = self.db.execute(select(Item).where(query.whereclause).with_only_columns(Item.id)).all()
        total_count = len(total)
            
        query = query.order_by(Item.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        items = self.db.execute(query).scalars().all()
        return items, total_count

    def update(self, item_id: int, user_id: int, item_data: ItemUpdate) -> Optional[Item]:
        item = self.get_by_id(item_id, user_id)
        if item:
            update_data = item_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(item, field, value)
            self.db.commit()
            self.db.refresh(item)
        return item

    def update_status(self, item_id: int, user_id: int, status: ItemStatus) -> Optional[Item]:
        item = self.get_by_id(item_id, user_id)
        if item:
            item.status = status
            item.updated_at = datetime.now(datetime.timezone.utc)
            self.db.commit()
            self.db.refresh(item)
        return item

    def delete(self, item_id: int, user_id: int) -> bool:
        item = self.get_by_id(item_id, user_id)
        if item:
            item.status = ItemStatus.DELETED
            item.updated_at = datetime.now(datetime.timezone.utc)
            self.db.commit()
            return True
        return False

    def hard_delete(self, item_id: int, user_id: int) -> bool:
        item = self.get_by_id(item_id, user_id)
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False