from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.auth import FirebaseUser
from app.repositories.user_repository import UserRepository


class UserService:
    """사용자 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def create_user(self, user_data: UserCreate) -> User:
        """새로운 사용자 생성 및 기본 포트폴리오 생성"""
        # 순환 참조 방지를 위해 함수 내에서 import
        from app.services.portfolio_service import PortfolioService
        from app.schemas.portfolio import PortfolioCreate

        try:
            db_user = self.user_repo.create(obj_in=user_data)

            # --- 기본 포트폴리오 생성 로직 ---
            portfolio_service = PortfolioService(self.db)
            default_portfolio_data = PortfolioCreate(
                name="My Portfolio",
                description="Default portfolio created on sign-up.",
                base_currency="USD",
            )
            portfolio_service.create_portfolio(
                user_id=db_user.uid, portfolio_data=default_portfolio_data
            )
            # ------------------------------------

            return db_user

        except IntegrityError:
            self.db.rollback()
            # 이미 존재하는 사용자인 경우 기존 사용자 반환
            existing_user = self.user_repo.get_by_uid(user_data.uid)
            if existing_user:
                return existing_user
            raise

    def get_user_by_uid(self, uid: str) -> Optional[User]:
        """UID로 사용자 조회"""
        return self.user_repo.get_by_uid(uid)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return self.user_repo.get_by_email(email)

    def update_user(self, uid: str, user_data: UserUpdate) -> Optional[User]:
        """사용자 정보 업데이트"""
        db_user = self.user_repo.get_by_uid(uid)
        if not db_user:
            return None

        updated_user = self.user_repo.update(
            db_obj=db_user, obj_in=user_data, updated_at=datetime.utcnow()
        )
        return updated_user

    def update_last_login(self, uid: str) -> Optional[User]:
        """마지막 로그인 시간 업데이트"""
        return self.user_repo.update_last_login(uid)

    def deactivate_user(self, uid: str) -> bool:
        """사용자 계정 비활성화"""
        return self.user_repo.deactivate_by_uid(uid)

    def get_or_create_user_from_firebase(self, firebase_user: FirebaseUser) -> User:
        """Firebase 유저 정보에서 사용자를 찾거나 생성"""
        # 기존 사용자 확인
        existing_user = self.user_repo.get_by_uid(firebase_user.uid)
        if existing_user:
            # 마지막 로그인 시간 업데이트
            self.update_last_login(firebase_user.uid)
            # 포트폴리오 정보를 별도로 로드
            from app.models.portfolio import Portfolio

            existing_user.portfolios = (
                self.db.query(Portfolio)
                .filter(Portfolio.user_id == firebase_user.uid)
                .all()
            )
            return existing_user

        # 새 사용자 생성
        user_data = UserCreate(
            uid=firebase_user.uid,
            email=firebase_user.email or f"{firebase_user.uid}@firebase.local",
            name=firebase_user.name,
            email_verified=True,  # Firebase에서 검증된 토큰이므로 True
        )

        new_user = self.create_user(user_data)
        # 새로 생성된 유저의 포트폴리오 정보를 별도로 로드
        from app.models.portfolio import Portfolio

        new_user.portfolios = (
            self.db.query(Portfolio).filter(Portfolio.user_id == new_user.uid).all()
        )
        return new_user
