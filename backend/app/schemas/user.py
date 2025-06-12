from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.portfolio import Portfolio as PortfolioSchema


class UserBase(BaseModel):
    """기본 사용자 정보"""

    email: EmailStr = Field(..., description="이메일 주소")
    name: Optional[str] = Field(None, max_length=100, description="사용자 이름")
    phone_number: Optional[str] = Field(None, max_length=20, description="전화번호")
    preferred_currency: str = Field("USD", max_length=3, description="선호 통화")
    timezone: str = Field("UTC", max_length=50, description="시간대")
    language: str = Field("ko", max_length=10, description="언어 설정")


class UserCreate(UserBase):
    """사용자 생성 시 사용하는 스키마"""

    uid: str = Field(..., max_length=128, description="Firebase UID")
    email_verified: bool = Field(False, description="이메일 인증 여부")


class UserUpdate(BaseModel):
    """사용자 정보 업데이트 시 사용하는 스키마"""

    name: Optional[str] = Field(None, max_length=100, description="사용자 이름")
    phone_number: Optional[str] = Field(None, max_length=20, description="전화번호")
    preferred_currency: Optional[str] = Field(
        None, max_length=3, description="선호 통화"
    )
    timezone: Optional[str] = Field(None, max_length=50, description="시간대")
    language: Optional[str] = Field(None, max_length=10, description="언어 설정")
    notification_settings: Optional[str] = Field(None, description="알림 설정 JSON")
    dashboard_settings: Optional[str] = Field(None, description="대시보드 설정 JSON")


class UserResponse(UserBase):
    """사용자 정보 응답 스키마"""

    uid: str
    email_verified: bool
    is_active: bool
    is_premium: bool
    notification_settings: Optional[str] = None
    dashboard_settings: Optional[str] = None
    portfolios: List[PortfolioSchema] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """사용자 프로필 정보 (공개용)"""

    uid: str
    name: Optional[str]
    phone_url: Optional[str]
    is_premium: bool
    created_at: datetime

    class Config:
        from_attributes = True
