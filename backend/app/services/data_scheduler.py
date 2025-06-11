import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, time
from dataclasses import dataclass
from enum import Enum
import aiocron

from app.services.providers.fred_provider import FREDProvider
from app.core.database import get_db
from app.models.economic_data import EconomicIndicatorRecord
from app.core.config import settings

logger = logging.getLogger(__name__)


class UpdateFrequency(Enum):
    """Data update frequencies for FRED indicators."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class IndicatorSchedule:
    """Configuration for each FRED indicator's update schedule."""

    indicator_code: str
    frequency: UpdateFrequency
    release_time: time  # Time when data is typically released
    release_day: Optional[int] = None  # Day of month for monthly data
    business_days_delay: int = 1  # Days to wait after release date


class FREDDataScheduler:
    """
    Scheduler for automatic FRED data updates based on each indicator's release schedule.

    FRED 지표별 갱신 주기:
    - 일일 데이터: 매일 오후 4:15 PM ET (다음날 오전 6시 KST에 체크)
    - 주간 데이터: 매주 목요일 오후 4:15 PM ET
    - 월간 데이터: 매월 특정일 오전 8:30 AM ET
    - 분기 데이터: 분기 말 익월 발표
    """

    # FRED 지표별 스케줄 설정
    INDICATOR_SCHEDULES = {
        # 채권 수익률 (일일)
        "DGS2": IndicatorSchedule(
            indicator_code="DGS2",
            frequency=UpdateFrequency.DAILY,
            release_time=time(6, 0),  # 6 AM KST (4:15 PM ET 다음날)
            business_days_delay=1,
        ),
        "DGS10": IndicatorSchedule(
            indicator_code="DGS10",
            frequency=UpdateFrequency.DAILY,
            release_time=time(6, 0),
            business_days_delay=1,
        ),
        "BAMLH0A0HYM2": IndicatorSchedule(
            indicator_code="BAMLH0A0HYM2",
            frequency=UpdateFrequency.DAILY,
            release_time=time(6, 0),
            business_days_delay=1,
        ),
        # 월간 지표들
        "UNRATE": IndicatorSchedule(  # 실업률 - 매월 첫째주 금요일
            indicator_code="UNRATE",
            frequency=UpdateFrequency.MONTHLY,
            release_time=time(22, 30),  # 8:30 AM ET = 10:30 PM KST (전날)
            release_day=6,  # 첫째주 금요일 근사치
            business_days_delay=1,
        ),
        "PAYEMS": IndicatorSchedule(  # 비농업 고용 - 매월 첫째주 금요일
            indicator_code="PAYEMS",
            frequency=UpdateFrequency.MONTHLY,
            release_time=time(22, 30),
            release_day=6,
            business_days_delay=1,
        ),
        "AHEPA": IndicatorSchedule(  # 평균 시급 - 매월 첫째주 금요일
            indicator_code="AHEPA",
            frequency=UpdateFrequency.MONTHLY,
            release_time=time(22, 30),
            release_day=6,
            business_days_delay=1,
        ),
        "CPIAUCSL": IndicatorSchedule(  # CPI - 매월 10~15일
            indicator_code="CPIAUCSL",
            frequency=UpdateFrequency.MONTHLY,
            release_time=time(22, 30),
            release_day=12,
            business_days_delay=1,
        ),
        "PPIACO": IndicatorSchedule(  # PPI - 매월 13~16일
            indicator_code="PPIACO",
            frequency=UpdateFrequency.MONTHLY,
            release_time=time(22, 30),
            release_day=14,
            business_days_delay=1,
        ),
        "T10YIE": IndicatorSchedule(  # 10년 기대인플레이션 - 일일
            indicator_code="T10YIE",
            frequency=UpdateFrequency.DAILY,
            release_time=time(6, 0),
            business_days_delay=1,
        ),
        "USACPIALL": IndicatorSchedule(  # 코어 CPI - 매월 10~15일
            indicator_code="USACPIALL",
            frequency=UpdateFrequency.MONTHLY,
            release_time=time(22, 30),
            release_day=12,
            business_days_delay=1,
        ),
        "M2SL": IndicatorSchedule(  # M2 통화공급량 - 매주 목요일
            indicator_code="M2SL",
            frequency=UpdateFrequency.WEEKLY,
            release_time=time(6, 0),
            business_days_delay=1,
        ),
        "FEDFUNDS": IndicatorSchedule(  # 연방기금금리 - 일일
            indicator_code="FEDFUNDS",
            frequency=UpdateFrequency.DAILY,
            release_time=time(6, 0),
            business_days_delay=1,
        ),
        "TEDRATE": IndicatorSchedule(  # TED 스프레드 - 일일
            indicator_code="TEDRATE",
            frequency=UpdateFrequency.DAILY,
            release_time=time(6, 0),
            business_days_delay=1,
        ),
        "STLFSI": IndicatorSchedule(  # 금융스트레스지수 - 주간
            indicator_code="STLFSI",
            frequency=UpdateFrequency.WEEKLY,
            release_time=time(6, 0),
            business_days_delay=1,
        ),
        "CLICKSA2": IndicatorSchedule(  # LEI - 매월 3주차
            indicator_code="CLICKSA2",
            frequency=UpdateFrequency.MONTHLY,
            release_time=time(22, 30),
            release_day=18,
            business_days_delay=1,
        ),
        "ICSBULL": IndicatorSchedule(  # 회사채 지수 - 월간
            indicator_code="ICSBULL",
            frequency=UpdateFrequency.MONTHLY,
            release_time=time(6, 0),
            release_day=1,
            business_days_delay=2,
        ),
    }

    def __init__(self):
        """Initialize FRED data scheduler."""
        self.fred_provider = FREDProvider()
        self.running_jobs = {}
        self.last_check_cache = {}

    async def start_scheduler(self) -> None:
        """Start all scheduled data update jobs."""
        logger.info("Starting FRED data scheduler...")

        # 일일 지표 체크 (매일 오전 6시)
        daily_job = aiocron.crontab("0 6 * * *", func=self.check_daily_indicators)
        self.running_jobs["daily"] = daily_job

        # 주간 지표 체크 (매주 목요일 오전 6시)
        weekly_job = aiocron.crontab("0 6 * * 4", func=self.check_weekly_indicators)
        self.running_jobs["weekly"] = weekly_job

        # 월간 지표 체크 (매일 오후 11시 - 월간 지표 확인용)
        monthly_job = aiocron.crontab("0 23 * * *", func=self.check_monthly_indicators)
        self.running_jobs["monthly"] = monthly_job

        # 즉시 한번 체크 수행
        await self.check_all_indicators()

        logger.info("FRED data scheduler started successfully")

    async def stop_scheduler(self) -> None:
        """Stop all scheduled jobs."""
        logger.info("Stopping FRED data scheduler...")

        for job_name, job in self.running_jobs.items():
            job.stop()
            logger.info(f"Stopped {job_name} job")

        self.running_jobs.clear()
        logger.info("FRED data scheduler stopped")

    async def check_daily_indicators(self) -> None:
        """Check and update daily indicators."""
        daily_indicators = [
            code
            for code, schedule in self.INDICATOR_SCHEDULES.items()
            if schedule.frequency == UpdateFrequency.DAILY
        ]

        logger.info(f"Checking daily indicators: {daily_indicators}")
        await self._update_indicators(daily_indicators)

    async def check_weekly_indicators(self) -> None:
        """Check and update weekly indicators."""
        weekly_indicators = [
            code
            for code, schedule in self.INDICATOR_SCHEDULES.items()
            if schedule.frequency == UpdateFrequency.WEEKLY
        ]

        logger.info(f"Checking weekly indicators: {weekly_indicators}")
        await self._update_indicators(weekly_indicators)

    async def check_monthly_indicators(self) -> None:
        """Check and update monthly indicators if release date has passed."""
        now = datetime.now()
        monthly_indicators = []

        for code, schedule in self.INDICATOR_SCHEDULES.items():
            if schedule.frequency == UpdateFrequency.MONTHLY:
                # 월간 지표의 발표일 확인
                if self._should_update_monthly_indicator(schedule, now):
                    monthly_indicators.append(code)

        if monthly_indicators:
            logger.info(f"Checking monthly indicators: {monthly_indicators}")
            await self._update_indicators(monthly_indicators)

    async def check_all_indicators(self) -> None:
        """Manually check all indicators for updates."""
        logger.info("Manual check of all FRED indicators")
        all_indicators = list(self.INDICATOR_SCHEDULES.keys())
        await self._update_indicators(all_indicators, force_update=True)

    async def _update_indicators(
        self, indicator_codes: List[str], force_update: bool = False
    ) -> None:
        """Update specified indicators if new data is available."""
        for indicator_code in indicator_codes:
            try:
                await self._update_single_indicator(indicator_code, force_update)
            except Exception as e:
                logger.error(f"Error updating indicator {indicator_code}: {e}")

    async def _update_single_indicator(
        self, indicator_code: str, force_update: bool = False
    ) -> None:
        """Update a single indicator if new data is available."""
        try:
            # 데이터베이스에서 마지막 업데이트 시간 확인
            last_update = await self._get_last_update_time(indicator_code)

            # FRED에서 최신 데이터 가져오기
            fred_data = await self.fred_provider.get_economic_series(indicator_code)

            if not fred_data:
                logger.warning(f"No data received for {indicator_code}")
                return

            # 새로운 데이터가 있는지 확인
            latest_data_date = fred_data.get("last_updated")
            if isinstance(latest_data_date, str):
                latest_data_date = datetime.fromisoformat(
                    latest_data_date.replace("Z", "+00:00")
                )

            # 업데이트 필요성 확인
            if not force_update and last_update and latest_data_date:
                if latest_data_date <= last_update:
                    logger.debug(f"No new data for {indicator_code}, skipping update")
                    return

            # 데이터베이스에 저장
            await self._save_indicator_data(indicator_code, fred_data)

            logger.info(f"Successfully updated {indicator_code} with latest data")

        except Exception as e:
            logger.error(f"Error updating indicator {indicator_code}: {e}")
            raise

    async def _get_last_update_time(self, indicator_code: str) -> Optional[datetime]:
        """Get the last update time for an indicator from database."""
        # TODO: 데이터베이스에서 마지막 업데이트 시간 조회
        # async with get_db() as db:
        #     result = await db.execute(
        #         select(EconomicIndicatorRecord.last_updated)
        #         .where(EconomicIndicatorRecord.indicator_code == indicator_code)
        #         .order_by(EconomicIndicatorRecord.last_updated.desc())
        #         .limit(1)
        #     )
        #     record = result.fetchone()
        #     return record.last_updated if record else None

        # 임시로 캐시에서 확인
        return self.last_check_cache.get(indicator_code)

    async def _save_indicator_data(
        self, indicator_code: str, data: Dict[str, Any]
    ) -> None:
        """Save indicator data to database."""
        # TODO: 데이터베이스에 저장 로직 구현
        # async with get_db() as db:
        #     record = EconomicIndicatorRecord(
        #         indicator_code=indicator_code,
        #         name=data.get('name'),
        #         value=data.get('value'),
        #         previous_value=data.get('previous_value'),
        #         unit=data.get('unit'),
        #         frequency=data.get('frequency'),
        #         source=data.get('source'),
        #         timestamp=data.get('timestamp'),
        #         last_updated=datetime.now()
        #     )
        #     db.add(record)
        #     await db.commit()

        # 임시로 캐시에 저장
        self.last_check_cache[indicator_code] = datetime.now()
        logger.info(f"Cached update time for {indicator_code}")

    def _should_update_monthly_indicator(
        self, schedule: IndicatorSchedule, now: datetime
    ) -> bool:
        """Check if monthly indicator should be updated based on release schedule."""
        if not schedule.release_day:
            return False

        # 이번 달의 발표일 계산
        release_date = datetime(now.year, now.month, schedule.release_day)

        # 발표일이 지났고, 업무일 딜레이를 고려한 날짜인지 확인
        update_date = release_date + timedelta(days=schedule.business_days_delay)

        return now >= update_date

    async def force_update_indicator(self, indicator_code: str) -> bool:
        """Force update a specific indicator."""
        try:
            await self._update_single_indicator(indicator_code, force_update=True)
            return True
        except Exception as e:
            logger.error(f"Error force updating {indicator_code}: {e}")
            return False

    async def get_update_status(self) -> Dict[str, Any]:
        """Get status of all scheduled indicators."""
        status = {
            "total_indicators": len(self.INDICATOR_SCHEDULES),
            "running_jobs": len(self.running_jobs),
            "last_checks": self.last_check_cache,
            "indicators_by_frequency": {
                "daily": len(
                    [
                        s
                        for s in self.INDICATOR_SCHEDULES.values()
                        if s.frequency == UpdateFrequency.DAILY
                    ]
                ),
                "weekly": len(
                    [
                        s
                        for s in self.INDICATOR_SCHEDULES.values()
                        if s.frequency == UpdateFrequency.WEEKLY
                    ]
                ),
                "monthly": len(
                    [
                        s
                        for s in self.INDICATOR_SCHEDULES.values()
                        if s.frequency == UpdateFrequency.MONTHLY
                    ]
                ),
            },
        }
        return status


# 전역 스케줄러 인스턴스
scheduler = FREDDataScheduler()
