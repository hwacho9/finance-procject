from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from datetime import datetime
import time
import logging

from app.services.market_data_service import (
    MarketDataService,
    create_market_data_service,
)
from app.schemas.market_schemas import (
    MarketIndicesResponse,
    MarketOverviewResponse,
    MarketIndexDetailResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["market-data"])


@router.get("/indices", response_model=MarketIndicesResponse)
async def get_market_indices(
    region: Optional[str] = Query(
        None, description="Region filter: US, EU, ASIA", regex="^(US|EU|ASIA)$"
    ),
    market_service: MarketDataService = Depends(create_market_data_service),
) -> MarketIndicesResponse:
    """
    Get current market indices data.

    - **region**: Optional region filter (US, EU, ASIA)
    - Returns market indices for the specified region or all regions if not specified
    """
    try:
        logger.info(f"Fetching market indices for region: {region}")
        return await market_service.get_indices(region)

    except Exception as e:
        logger.error(f"Error fetching market indices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch market indices data",
        )


@router.get("/test-indices")
async def test_specific_indices(
    market_service: MarketDataService = Depends(create_market_data_service),
):
    """
    Test specific indices mentioned by the user.
    Tests VIX, VXN, VSTOXX, VKOSPI and major market indices.
    """
    # Test symbols as requested by user
    test_symbols = {
        "volatility": ["VIX", "VXN", "VSTOXX", "VKOSPI"],
        "us_indices": ["DJIA", "SP500", "NASDAQ", "RUSSELL2000", "PHLX_SOX"],
        "japan": ["NIKKEI225", "TOPIX"],
        "korea": ["KOSPI", "KOSDAQ"],
        "hong_kong": ["HANG_SENG"],
    }

    results = {}

    for category, symbols in test_symbols.items():
        results[category] = {}
        for symbol in symbols:
            try:
                quote_data = await market_service.get_quote(symbol)
                results[category][symbol] = {"status": "success", "data": quote_data}
            except Exception as e:
                results[category][symbol] = {"status": "error", "error": str(e)}

    return {
        "message": "Test of specific indices requested by user",
        "results": results,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/indices/{symbol}", response_model=MarketIndexDetailResponse)
async def get_index_detail(
    symbol: str,
    period: str = Query(
        "1d",
        description="Time period for historical data",
        regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$",
    ),
    market_service: MarketDataService = Depends(create_market_data_service),
) -> MarketIndexDetailResponse:
    """
    Get detailed data for a specific market index.

    - **symbol**: Index symbol (e.g., SP500, DJIA, NASDAQ)
    - **period**: Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    """
    try:
        logger.info(f"Fetching index detail for {symbol} with period {period}")
        return await market_service.get_index_detail(symbol, period)

    except Exception as e:
        logger.error(f"Error fetching index detail for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch data for index {symbol}",
        )


@router.get("/quote/{symbol}")
async def get_quote(
    symbol: str,
    market_service: MarketDataService = Depends(create_market_data_service),
) -> JSONResponse:
    """
    Get quote data for a specific market index.

    - **symbol**: Index symbol (e.g., SP500, DJIA, NASDAQ)
    """
    try:
        logger.info(f"Fetching quote for {symbol}")
        quote_data = await market_service.get_quote(symbol)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success", "data": quote_data},
        )

    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch quote for index {symbol}",
        )


@router.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview(
    market_service: MarketDataService = Depends(create_market_data_service),
) -> MarketOverviewResponse:
    """
    Get comprehensive market overview including indices, bonds, commodities, and currencies.

    - Returns complete market snapshot with all available data
    """
    try:
        logger.info("Fetching market overview")
        return await market_service.get_market_overview()

    except Exception as e:
        logger.error(f"Error fetching market overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch market overview",
        )


@router.post("/refresh")
async def refresh_market_data(
    region: Optional[str] = Query(
        None, description="Region to refresh cache for", regex="^(US|EU|ASIA)$"
    ),
    market_service: MarketDataService = Depends(create_market_data_service),
) -> JSONResponse:
    """
    Force refresh of cached market data.

    - **region**: Optional region to refresh (US, EU, ASIA)
    - Clears cache and fetches fresh data from providers
    """
    try:
        logger.info(f"Refreshing market data cache for region: {region}")
        success = await market_service.refresh_cache(region)

        if success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": f"Successfully refreshed market data cache for region: {region or 'all'}",
                    "region": region,
                    "timestamp": str(datetime.now()),
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to refresh market data cache",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing market data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh market data",
        )


@router.get("/health")
async def market_data_health_check(
    market_service: MarketDataService = Depends(create_market_data_service),
) -> JSONResponse:
    """
    Health check endpoint for market data service.

    - Tests connection to data providers
    - Returns service status and response times
    """
    try:
        start_time = time.time()

        # Try to fetch a simple quote to test provider connectivity
        test_data = await market_service.get_index_detail("SP500", "1d")

        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "service": "market-data",
                "response_time_ms": round(response_time, 2),
                "last_check": str(datetime.now()),
                "provider_status": "connected",
            },
        )

    except Exception as e:
        logger.error(f"Market data health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "market-data",
                "error": str(e),
                "last_check": str(datetime.now()),
                "provider_status": "disconnected",
            },
        )
