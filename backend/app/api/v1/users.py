from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_sync_db
from app.core.auth import get_current_user, FirebaseUser
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserUpdate, UserProfile


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """현재 로그인한 사용자 정보 조회"""
    user_service = UserService(db)

    # Firebase 사용자 정보에서 DB 사용자 정보 가져오거나 생성
    db_user = user_service.get_or_create_user_from_firebase(current_user)

    return db_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """현재 로그인한 사용자 정보 업데이트"""
    user_service = UserService(db)

    # 사용자가 존재하는지 확인
    existing_user = user_service.get_user_by_uid(current_user.uid)
    if not existing_user:
        # 사용자가 없으면 먼저 생성
        existing_user = user_service.get_or_create_user_from_firebase(current_user)

    # 사용자 정보 업데이트
    updated_user = user_service.update_user(current_user.uid, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다."
        )

    return updated_user


@router.get("/profile/{uid}", response_model=UserProfile)
async def get_user_profile(
    uid: str,
    db: Session = Depends(get_sync_db),
):
    """사용자 공개 프로필 조회"""
    user_service = UserService(db)

    user = user_service.get_user_by_uid(uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="비활성화된 사용자입니다."
        )

    return user


@router.delete("/me")
async def deactivate_current_user(
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """현재 로그인한 사용자 계정 비활성화"""
    user_service = UserService(db)

    success = user_service.deactivate_user(current_user.uid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다."
        )

    return {"message": "계정이 비활성화되었습니다."}
