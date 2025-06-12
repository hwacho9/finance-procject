from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """
    사용자 정보를 저장하는 테이블.
    Firebase Authentication과 연동하여 추가 사용자 정보를 저장
    """

    __tablename__ = "users"

    # Firebase UID를 primary key로 사용
    uid = Column(String(128), primary_key=True, index=True, comment="Firebase UID")

    # Relationships
    portfolios = relationship(
        "Portfolio", back_populates="user", cascade="all, delete-orphan"
    )

    # 기본 정보
    email = Column(
        String(255), unique=True, index=True, nullable=False, comment="이메일 주소"
    )
    name = Column(String(100), nullable=True, comment="사용자 이름")

    # 계정 상태
    email_verified = Column(Boolean, default=False, comment="이메일 인증 여부")
    is_active = Column(Boolean, default=True, comment="계정 활성화 상태")
    is_premium = Column(Boolean, default=False, comment="프리미엄 회원 여부")

    # 추가 프로필 정보
    phone_number = Column(String(20), nullable=True, comment="전화번호")
    preferred_currency = Column(String(3), default="USD", comment="선호 통화")
    timezone = Column(String(50), default="UTC", comment="시간대")
    language = Column(String(10), default="ko", comment="언어 설정")

    # 개인화 설정
    notification_settings = Column(Text, nullable=True, comment="알림 설정 JSON")
    dashboard_settings = Column(Text, nullable=True, comment="대시보드 설정 JSON")

    # 시간 정보
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="계정 생성일"
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), comment="마지막 수정일"
    )
    last_login_at = Column(
        DateTime(timezone=True), nullable=True, comment="마지막 로그인일"
    )

    def __repr__(self):
        return f"<User(uid={self.uid}, email={self.email}, name={self.name})>"
