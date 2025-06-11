from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse
import logging

from app.services.economic_data_service import (
    EconomicDataService,
    create_economic_data_service,
)
from app.schemas.economic_schemas import (
    EconomicIndicatorsResponse,
    EconomicIndicatorDetailResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/economic", tags=["economic-data"])


@router.get("/indicators", response_model=EconomicIndicatorsResponse)
async def get_economic_indicators(
    economic_service: EconomicDataService = Depends(create_economic_data_service),
) -> EconomicIndicatorsResponse:
    """
    Get all economic indicators.

    - Returns comprehensive economic data including employment, inflation, monetary policy, etc.
    """
    try:
        logger.info("Fetching all economic indicators")
        return await economic_service.get_all_indicators()

    except Exception as e:
        logger.error(f"Error fetching economic indicators: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch economic indicators",
        )


@router.get(
    "/indicators/{indicator_code}", response_model=EconomicIndicatorDetailResponse
)
async def get_indicator_detail(
    indicator_code: str,
    economic_service: EconomicDataService = Depends(create_economic_data_service),
) -> EconomicIndicatorDetailResponse:
    """
    Get detailed data for a specific economic indicator.

    - **indicator_code**: FRED series ID (e.g., DGS10, UNRATE, CPIAUCSL)
    """
    try:
        logger.info(f"Fetching indicator detail for {indicator_code}")
        return await economic_service.get_indicator_detail(indicator_code)

    except Exception as e:
        logger.error(f"Error fetching indicator detail for {indicator_code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch data for indicator {indicator_code}",
        )


@router.get("/indicators/category/{category}")
async def get_indicators_by_category(
    category: str = Path(
        ...,
        description="Indicator category",
        regex="^(bonds|employment|inflation|monetary|financial_stability|leading_indicators)$",
    ),
    economic_service: EconomicDataService = Depends(create_economic_data_service),
):
    """
    Get economic indicators by category.

    - **category**: Category of indicators (bonds, employment, inflation, monetary, financial_stability, leading_indicators)
    """
    try:
        logger.info(f"Fetching economic indicators for category: {category}")
        return await economic_service.get_indicators_by_category(category)

    except Exception as e:
        logger.error(f"Error fetching indicators for category {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch indicators for category {category}",
        )


@router.get("/bonds")
async def get_bonds_data(
    economic_service: EconomicDataService = Depends(create_economic_data_service),
):
    """
    Get bond market indicators.

    - **DGS2**: 2-Year Treasury Rate
    - **DGS10**: 10-Year Treasury Rate
    - **ICSBULL**: ICE BofA US Corporate Bond Index
    - **BAMLH0A0HYM2**: ICE BofA High Yield Master II Index
    """
    try:
        logger.info("Fetching bond market indicators")
        return await economic_service.get_bonds_data()

    except Exception as e:
        logger.error(f"Error fetching bond data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bond market data",
        )


@router.get("/employment")
async def get_employment_data(
    economic_service: EconomicDataService = Depends(create_economic_data_service),
):
    """
    Get employment indicators.

    - **UNRATE**: Unemployment Rate
    - **PAYEMS**: Nonfarm Payrolls
    - **AHEPA**: Average Hourly Earnings
    """
    try:
        logger.info("Fetching employment indicators")
        return await economic_service.get_employment_data()

    except Exception as e:
        logger.error(f"Error fetching employment data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch employment data",
        )


@router.get("/inflation")
async def get_inflation_data(
    economic_service: EconomicDataService = Depends(create_economic_data_service),
):
    """
    Get inflation indicators.

    - **CPIAUCSL**: Consumer Price Index
    - **PPIACO**: Producer Price Index
    - **T10YIE**: 10-Year Breakeven Inflation Rate
    - **USACPIALL**: Core CPI
    """
    try:
        logger.info("Fetching inflation indicators")
        return await economic_service.get_inflation_data()

    except Exception as e:
        logger.error(f"Error fetching inflation data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch inflation data",
        )


@router.get("/monetary")
async def get_monetary_data(
    economic_service: EconomicDataService = Depends(create_economic_data_service),
):
    """
    Get monetary policy indicators.

    - **FEDFUNDS**: Federal Funds Rate
    - **M2SL**: M2 Money Supply
    """
    try:
        logger.info("Fetching monetary policy indicators")
        return await economic_service.get_monetary_data()

    except Exception as e:
        logger.error(f"Error fetching monetary data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch monetary policy data",
        )


@router.get("/financial-stability")
async def get_financial_stability_data(
    economic_service: EconomicDataService = Depends(create_economic_data_service),
):
    """
    Get financial stability indicators.

    - **TEDRATE**: TED Spread
    - **STLFSI**: St. Louis Fed Financial Stress Index
    """
    try:
        logger.info("Fetching financial stability indicators")
        return await economic_service.get_financial_stability_data()

    except Exception as e:
        logger.error(f"Error fetching financial stability data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch financial stability data",
        )


@router.post("/refresh")
async def refresh_economic_data(
    category: Optional[str] = Query(
        None,
        description="Category to refresh cache for",
        regex="^(bonds|employment|inflation|monetary|financial_stability|leading_indicators)$",
    ),
    economic_service: EconomicDataService = Depends(create_economic_data_service),
) -> JSONResponse:
    """
    Force refresh of cached economic data.

    - **category**: Optional category to refresh (bonds, employment, inflation, monetary, financial_stability, leading_indicators)
    - Clears cache and fetches fresh data from FRED
    """
    try:
        logger.info(f"Refreshing economic data cache for category: {category}")
        success = await economic_service.refresh_cache(category)

        if success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": f"Successfully refreshed economic data cache for category: {category or 'all'}",
                    "category": category,
                    "timestamp": str(datetime.now()),
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to refresh economic data cache",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing economic data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh economic data",
        )


@router.get("/health")
async def economic_data_health_check(
    economic_service: EconomicDataService = Depends(create_economic_data_service),
) -> JSONResponse:
    """
    Health check endpoint for economic data service.

    - Tests connection to FRED API
    - Returns service status and response times
    """
    try:
        start_time = time.time()

        # Try to fetch a simple indicator to test FRED connectivity
        test_data = await economic_service.get_indicator_detail("DGS10")

        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "service": "economic-data",
                "provider": "FRED",
                "response_time_ms": round(response_time, 2),
                "last_check": str(datetime.now()),
                "provider_status": "connected",
                "test_indicator": test_data.indicator.indicator_code,
            },
        )

    except Exception as e:
        logger.error(f"Economic data health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "economic-data",
                "provider": "FRED",
                "error": str(e),
                "last_check": str(datetime.now()),
                "provider_status": "disconnected",
            },
        )


# Import necessary modules for the endpoints
from datetime import datetime
import time
