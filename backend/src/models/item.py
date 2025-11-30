from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, ARRAY, Index
from sqlalchemy.orm import relationship
from src.models.base import Base, utc_now
from src.schemas.item import ItemStatus

class Item(Base):
    """Modelo de Item para armazenamento no banco de dados"""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)
    item_type = Column(String(50), nullable=False)
    primary_color = Column(String(50), nullable=False)
    usage = Column(String(50), nullable=False)
    texture = Column(String(50), nullable=False)
    print_category = Column(String(50), nullable=False)
    image_url = Column(String(500), nullable=False)
    ownership = Column(Boolean, nullable=False, default=True, index=True)
    status = Column(
        SQLEnum(ItemStatus), 
        nullable=False, 
        default=ItemStatus.ACTIVE,
        index=True
    )

    # Relacionamentos
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="items")

    # Campos de auditoria
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    # Índices compostos para queries comuns
    __table_args__ = (
        Index('idx_user_category', 'user_id', 'category'),
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_user_ownership', 'user_id', 'ownership'),
    )

    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', category='{self.category}', user_id={self.user_id})>"
