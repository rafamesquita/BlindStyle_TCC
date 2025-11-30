from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base, utc_now

class Suggestion(Base):
    """Modelo de Sugestão para armazenamento no banco de dados"""
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    outfit1 = Column(String(1000), nullable=True)
    outfit2 = Column(String(1000), nullable=True)
    outfit3 = Column(String(1000), nullable=True)

    # Relacionamentos
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="suggestions")
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    item = relationship("Item")

    # Campos de auditoria
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    def __repr__(self):
        return f"<Suggestion(id={self.id}, user_id={self.user_id}, item_id={self.item_id})>"