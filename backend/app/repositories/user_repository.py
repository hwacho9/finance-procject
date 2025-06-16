from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User repository with specific business logic"""

    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_uid(self, uid: str) -> Optional[User]:
        """Get user by Firebase UID"""
        return self.db.query(User).filter(User.uid == uid).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_active_users(self) -> list[User]:
        """Get all active users"""
        return self.db.query(User).filter(User.is_active == True).all()

    def deactivate_by_uid(self, uid: str) -> bool:
        """Deactivate user by UID"""
        user = self.get_by_uid(uid)
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False

    def update_last_login(self, uid: str) -> Optional[User]:
        """Update user's last login timestamp"""
        from datetime import datetime

        user = self.get_by_uid(uid)
        if user:
            user.last_login_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            return user
        return None
