from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Index
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class EconomicIndicatorRecord(Base):
    """
    경제 지표 데이터를 저장하는 테이블.

    FRED API에서 가져온 경제 지표의 과거 및 현재 데이터를 타임시리즈로 저장
    """

    __tablename__ = "economic_indicators"

    id = Column(Integer, primary_key=True, index=True)

    # 지표 식별 정보
    indicator_code = Column(
        String(50),
        index=True,
        nullable=False,
        comment="FRED 지표 코드 (예: DGS10, UNRATE)",
    )
    name = Column(String(500), nullable=False, comment="지표 전체 이름")
    category = Column(
        String(100),
        index=True,
        comment="지표 카테고리 (bonds, employment, inflation 등)",
    )

    # 지표 값 정보
    value = Column(Float, nullable=False, comment="지표 값")
    previous_value = Column(Float, nullable=True, comment="이전 기간 값")
    change = Column(Float, nullable=True, comment="변화량")
    change_percent = Column(Float, nullable=True, comment="변화율 (%)")

    # 메타데이터
    unit = Column(
        String(100), nullable=False, comment="단위 (Percent, Index, Billions 등)"
    )
    frequency = Column(
        String(50),
        nullable=False,
        comment="발표 주기 (daily, weekly, monthly, quarterly)",
    )
    source = Column(String(100), default="FRED", comment="데이터 소스")
    country = Column(String(10), default="US", comment="국가 코드")

    # 시간 정보
    data_date = Column(DateTime, nullable=False, comment="데이터 기준일")
    timestamp = Column(DateTime, default=func.now(), comment="API 조회 시각")
    last_updated = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        comment="마지막 업데이트 시각",
    )

    # 추가 정보
    notes = Column(Text, nullable=True, comment="지표 관련 메모")

    # 인덱스 설정
    __table_args__ = (
        Index("idx_indicator_date", "indicator_code", "data_date"),
        Index("idx_category_date", "category", "data_date"),
        Index("idx_timestamp", "timestamp"),
    )

    def __repr__(self):
        return f"<EconomicIndicator(code={self.indicator_code}, value={self.value}, date={self.data_date})>"


class IndicatorUpdateLog(Base):
    """
    지표 업데이트 로그를 기록하는 테이블.

    스케줄러가 언제 어떤 지표를 업데이트했는지 추적
    """

    __tablename__ = "indicator_update_logs"

    id = Column(Integer, primary_key=True, index=True)

    indicator_code = Column(String(50), index=True, nullable=False)
    update_type = Column(String(50), nullable=False, comment="scheduled, manual, force")
    status = Column(String(50), nullable=False, comment="success, failed, skipped")

    # 업데이트 결과
    records_updated = Column(Integer, default=0, comment="업데이트된 레코드 수")
    latest_data_date = Column(
        DateTime, nullable=True, comment="가장 최신 데이터의 기준일"
    )
    error_message = Column(Text, nullable=True, comment="오류 메시지 (실패시)")

    # 시간 정보
    started_at = Column(DateTime, default=func.now(), comment="업데이트 시작 시각")
    completed_at = Column(DateTime, nullable=True, comment="업데이트 완료 시각")
    duration_seconds = Column(Float, nullable=True, comment="소요 시간 (초)")

    # 인덱스 설정
    __table_args__ = (
        Index("idx_update_indicator_date", "indicator_code", "started_at"),
        Index("idx_update_status", "status", "started_at"),
    )

    def __repr__(self):
        return f"<UpdateLog(code={self.indicator_code}, status={self.status}, started={self.started_at})>"


class DataQualityCheck(Base):
    """
    데이터 품질 체크 결과를 저장하는 테이블.

    FRED 데이터의 이상값, 누락값 등을 모니터링
    """

    __tablename__ = "data_quality_checks"

    id = Column(Integer, primary_key=True, index=True)

    indicator_code = Column(String(50), index=True, nullable=False)
    check_type = Column(
        String(100),
        nullable=False,
        comment="missing_data, outlier, validation_error 등",
    )
    severity = Column(String(50), nullable=False, comment="low, medium, high, critical")

    # 체크 결과
    status = Column(String(50), nullable=False, comment="pass, warning, fail")
    message = Column(Text, nullable=False, comment="체크 결과 메시지")
    affected_data_date = Column(
        DateTime, nullable=True, comment="문제가 발견된 데이터 기준일"
    )

    # 시간 정보
    checked_at = Column(DateTime, default=func.now(), comment="체크 수행 시각")
    resolved_at = Column(DateTime, nullable=True, comment="문제 해결 시각")

    # 인덱스 설정
    __table_args__ = (
        Index("idx_quality_indicator_date", "indicator_code", "checked_at"),
        Index("idx_quality_severity", "severity", "status"),
    )
