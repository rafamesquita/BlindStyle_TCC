from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from src.models.base import Base, utc_now

class AuthProvider(PyEnum):
    """Provedores de autenticação suportados"""
    LOCAL = "local"  # Para autenticação tradicional
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    APPLE = "apple"

class User(Base):
    """Modelo de usuário com suporte a autenticação local e OAuth"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    picture = Column(String(1000), nullable=True)  # URL da foto do perfil
    
    # Campos para autenticação local
    hashed_password = Column(String(255), nullable=True)  # Pode ser nulo para usuários OAuth
    
    # Campos para OAuth
    auth_provider = Column(SQLEnum(AuthProvider), nullable=False, default=AuthProvider.LOCAL, index=True)
    provider_user_id = Column(String(255), nullable=True)  # ID único do provedor (nulo para auth local)
    access_token = Column(String(2000), nullable=True)
    refresh_token = Column(String(2000), nullable=True)
    token_expires = Column(DateTime, nullable=True)
    
    # Campos comuns
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now) 
    last_login = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    
    # Relacionamentos
    items = relationship("Item", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    suggestions = relationship("Suggestion", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")

    # Índice composto para busca por provider
    __table_args__ = (
        Index('idx_provider_user', 'auth_provider', 'provider_user_id'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', provider={self.auth_provider.value})>"