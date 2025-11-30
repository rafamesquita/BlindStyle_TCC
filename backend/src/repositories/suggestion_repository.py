from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models.suggestion import Suggestion


class SuggestionRepository:
    """Repository para operações de banco de dados com Suggestions"""
    
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        item_id: int,
        outfit1: Optional[str] = None,
        outfit2: Optional[str] = None,
        outfit3: Optional[str] = None
    ) -> Suggestion:
        """
        Cria uma nova sugestão no banco de dados
        
        Args:
            user_id: ID do usuário
            item_id: ID do item para o qual foram geradas as sugestões
            outfit1: CSV com paths das imagens do outfit 1
            outfit2: CSV com paths das imagens do outfit 2
            outfit3: CSV com paths das imagens do outfit 3
            
        Returns:
            Suggestion: Objeto Suggestion criado
        """
        db_suggestion = Suggestion(
            user_id=user_id,
            item_id=item_id,
            outfit1=outfit1,
            outfit2=outfit2,
            outfit3=outfit3
        )
        self.db.add(db_suggestion)
        self.db.commit()
        self.db.refresh(db_suggestion)
        return db_suggestion

    def get_by_id(self, suggestion_id: int) -> Optional[Suggestion]:
        """Busca uma sugestão pelo ID"""
        query = select(Suggestion).where(Suggestion.id == suggestion_id)
        return self.db.execute(query).scalar_one_or_none()

    def get_by_user_and_item(
        self, 
        user_id: int, 
        item_id: int
    ) -> Optional[Suggestion]:
        """
        Busca a sugestão mais recente para um usuário e item específicos
        
        Args:
            user_id: ID do usuário
            item_id: ID do item
            
        Returns:
            Suggestion mais recente ou None
        """
        query = (
            select(Suggestion)
            .where(Suggestion.user_id == user_id)
            .where(Suggestion.item_id == item_id)
            .order_by(Suggestion.created_at.desc())
        )
        return self.db.execute(query).scalars().first()

    def list_by_user(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[Suggestion]:
        """
        Lista todas as sugestões de um usuário
        
        Args:
            user_id: ID do usuário
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de Suggestions
        """
        query = (
            select(Suggestion)
            .where(Suggestion.user_id == user_id)
            .order_by(Suggestion.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.db.execute(query).scalars().all()

    def delete(self, suggestion_id: int) -> bool:
        """
        Remove uma sugestão do banco de dados
        
        Args:
            suggestion_id: ID da sugestão
            
        Returns:
            bool: True se deletado com sucesso, False caso contrário
        """
        suggestion = self.get_by_id(suggestion_id)
        if suggestion:
            self.db.delete(suggestion)
            self.db.commit()
            return True
        return False
