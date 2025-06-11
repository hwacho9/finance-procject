from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from app.services.data_scheduler import scheduler, FREDDataScheduler

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status")
async def get_scheduler_status() -> Dict[str, Any]:
    """
    Get current status of FRED data scheduler.

    Returns information about:
    - Running jobs count
    - Last update times for each indicator
    - Indicators count by frequency
    """
    try:
        status = await scheduler.get_update_status()

        return {
            "scheduler_status": "running" if scheduler.running_jobs else "stopped",
            "total_indicators": status["total_indicators"],
            "running_jobs": status["running_jobs"],
            "indicators_by_frequency": status["indicators_by_frequency"],
            "last_checks": {
                code: time.isoformat() if time else None
                for code, time in status["last_checks"].items()
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scheduler status",
        )


@router.post("/start")
async def start_scheduler(background_tasks: BackgroundTasks) -> JSONResponse:
    """
    Start the FRED data scheduler.

    Starts cron jobs for:
    - Daily indicators: 6 AM KST
    - Weekly indicators: Every Thursday 6 AM KST
    - Monthly indicators: Daily check at 11 PM KST
    """
    try:
        if scheduler.running_jobs:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Scheduler is already running",
                    "running_jobs": len(scheduler.running_jobs),
                    "timestamp": datetime.now().isoformat(),
                },
            )

        background_tasks.add_task(scheduler.start_scheduler)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "FRED data scheduler started successfully",
                "scheduled_jobs": ["daily", "weekly", "monthly"],
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start scheduler",
        )


@router.post("/stop")
async def stop_scheduler() -> JSONResponse:
    """
    Stop the FRED data scheduler.

    Stops all running cron jobs.
    """
    try:
        if not scheduler.running_jobs:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Scheduler is not running",
                    "timestamp": datetime.now().isoformat(),
                },
            )

        await scheduler.stop_scheduler()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "FRED data scheduler stopped successfully",
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop scheduler",
        )


@router.post("/update/manual")
async def manual_update_all(background_tasks: BackgroundTasks) -> JSONResponse:
    """
    Manually trigger update for all FRED indicators.

    Forces update of all indicators regardless of schedule.
    """
    try:
        background_tasks.add_task(scheduler.check_all_indicators)

        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "message": "Manual update triggered for all FRED indicators",
                "total_indicators": len(scheduler.INDICATOR_SCHEDULES),
                "timestamp": datetime.now().isoformat(),
                "note": "Update is running in background. Check status endpoint for progress.",
            },
        )

    except Exception as e:
        logger.error(f"Error triggering manual update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger manual update",
        )


@router.post("/update/indicator/{indicator_code}")
async def force_update_indicator(
    indicator_code: str, background_tasks: BackgroundTasks
) -> JSONResponse:
    """
    Force update a specific FRED indicator.

    - **indicator_code**: FRED series ID (e.g., DGS10, UNRATE, CPIAUCSL)
    """
    try:
        if indicator_code not in scheduler.INDICATOR_SCHEDULES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Indicator {indicator_code} not found in scheduler configuration",
            )

        background_tasks.add_task(scheduler.force_update_indicator, indicator_code)

        schedule_info = scheduler.INDICATOR_SCHEDULES[indicator_code]

        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "message": f"Force update triggered for indicator {indicator_code}",
                "indicator_code": indicator_code,
                "frequency": schedule_info.frequency.value,
                "timestamp": datetime.now().isoformat(),
                "note": "Update is running in background. Check status endpoint for progress.",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error force updating indicator {indicator_code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to force update indicator {indicator_code}",
        )


@router.get("/schedules")
async def get_indicator_schedules() -> Dict[str, Any]:
    """
    Get schedule configuration for all FRED indicators.

    Returns update frequency and timing for each indicator.
    """
    try:
        schedules = {}

        for code, schedule in scheduler.INDICATOR_SCHEDULES.items():
            schedules[code] = {
                "indicator_code": schedule.indicator_code,
                "frequency": schedule.frequency.value,
                "release_time": schedule.release_time.strftime("%H:%M"),
                "release_day": schedule.release_day,
                "business_days_delay": schedule.business_days_delay,
            }

        # 주기별 통계
        frequency_stats = {}
        for freq in ["daily", "weekly", "monthly", "quarterly"]:
            frequency_stats[freq] = len(
                [
                    s
                    for s in scheduler.INDICATOR_SCHEDULES.values()
                    if s.frequency.value == freq
                ]
            )

        return {
            "total_indicators": len(scheduler.INDICATOR_SCHEDULES),
            "schedules": schedules,
            "frequency_statistics": frequency_stats,
            "timezone": "KST (Korea Standard Time)",
            "notes": {
                "daily": "Updated every business day at 6 AM KST",
                "weekly": "Updated every Thursday at 6 AM KST",
                "monthly": "Checked daily at 11 PM KST, updated when release date passes",
            },
        }

    except Exception as e:
        logger.error(f"Error getting indicator schedules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get indicator schedules",
        )


@router.get("/health")
async def scheduler_health_check() -> JSONResponse:
    """
    Health check for FRED data scheduler.

    Checks if scheduler is properly configured and running.
    """
    try:
        status_info = await scheduler.get_update_status()

        health_status = {
            "status": "healthy" if scheduler.running_jobs else "idle",
            "configured_indicators": status_info["total_indicators"],
            "running_jobs": status_info["running_jobs"],
            "last_activity": None,
            "timestamp": datetime.now().isoformat(),
        }

        # 마지막 활동 시간 찾기
        if status_info["last_checks"]:
            latest_check = max(status_info["last_checks"].values())
            health_status["last_activity"] = latest_check.isoformat()

        return JSONResponse(status_code=status.HTTP_200_OK, content=health_status)

    except Exception as e:
        logger.error(f"Scheduler health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        )
