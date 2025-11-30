from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.repositories.base_repository import BaseRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        self.db = db
        self.model = User

    def get_by_id(self, id: int) -> Optional[User]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def getUserByEmail(self, email: str) -> Optional[User]:
        return self.db.query(self.model).filter(self.model.email == email).first()

    def get_all(self) -> List[User]:
        return self.db.query(self.model).all()

    def create(self, user: UserCreate) -> User:
        # Truncate password to 72 bytes to comply with bcrypt limit
        password_bytes = user.password.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError(f"Password too long. Maximum length is 72 bytes. {password_bytes.decode('utf-8', errors='ignore')}")
        
        hashed_password = pwd_context.hash(password_bytes)
        new_user = User(
            email=user.email,
            name=user.name,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.utcnow()
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_update.dict(exclude_unset=True)
        
        if "password" in update_data:
            password = update_data.pop("password")
            # Truncate password to 72 bytes to comply with bcrypt limit
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
                password = password_bytes.decode('utf-8', errors='ignore')
            update_data["hashed_password"] = pwd_context.hash(password)

        for key, value in update_data.items():
            setattr(db_user, key, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete(self, user_id: int) -> bool:
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        return True

    def verify_password(self, user: User, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, user.hashed_password)

    def update_refresh_token(self, user_id: int, refresh_token: str) -> None:
        db_user = self.get_by_id(user_id)
        if db_user:
            db_user.refresh_token = refresh_token
            self.db.commit()