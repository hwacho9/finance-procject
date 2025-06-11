import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from fredapi import Fred

from app.services.providers.base import EconomicDataProvider, DataTransformer
from app.core.config import settings

logger = logging.getLogger(__name__)


class FREDProvider(EconomicDataProvider):
    """FRED (Federal Reserve Economic Data) provider implementation."""

    # FRED 지표 매핑
    FRED_SERIES_MAPPING = {
        # 채권 수익률
        "DGS2": {
            "name": "2-Year Treasury Constant Maturity Rate",
            "unit": "Percent",
            "category": "bonds",
        },
        "DGS10": {
            "name": "10-Year Treasury Constant Maturity Rate",
            "unit": "Percent",
            "category": "bonds",
        },
        "ICSBULL": {
            "name": "ICE BofA US Corporate Bond Index",
            "unit": "Index",
            "category": "bonds",
        },
        "BAMLH0A0HYM2": {
            "name": "ICE BofA High Yield Master II Index",
            "unit": "Percent",
            "category": "bonds",
        },
        # 고용 지표
        "UNRATE": {
            "name": "Unemployment Rate",
            "unit": "Percent",
            "category": "employment",
        },
        "PAYEMS": {
            "name": "All Employees, Total Nonfarm",
            "unit": "Thousands of Persons",
            "category": "employment",
        },
        "AHEPA": {
            "name": "Average Hourly Earnings of All Employees",
            "unit": "Dollars per Hour",
            "category": "employment",
        },
        # 인플레이션 지표
        "CPIAUCSL": {
            "name": "Consumer Price Index for All Urban Consumers: All Items in U.S. City Average",
            "unit": "Index",
            "category": "inflation",
        },
        "PPIACO": {
            "name": "Producer Price Index by Commodity: All Commodities",
            "unit": "Index",
            "category": "inflation",
        },
        "T10YIE": {
            "name": "10-Year Breakeven Inflation Rate",
            "unit": "Percent",
            "category": "inflation",
        },
        "USACPIALL": {
            "name": "Consumer Price Index: Total All Items for the United States",
            "unit": "Index",
            "category": "inflation",
        },
        # 선행·동행지수
        "CLICKSA2": {
            "name": "Conference Board Leading Economic Index",
            "unit": "Index",
            "category": "leading_indicators",
        },
        # 통화 지표
        "M2SL": {
            "name": "M2 Money Stock",
            "unit": "Billions of Dollars",
            "category": "monetary",
        },
        "FEDFUNDS": {
            "name": "Federal Funds Effective Rate",
            "unit": "Percent",
            "category": "monetary",
        },
        # 금융안정성
        "TEDRATE": {
            "name": "TED Spread",
            "unit": "Percent",
            "category": "financial_stability",
        },
        "STLFSI": {
            "name": "St. Louis Fed Financial Stress Index",
            "unit": "Index",
            "category": "financial_stability",
        },
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize FRED provider with API key."""
        self.api_key = api_key or settings.fred_api_key
        if not self.api_key:
            logger.warning("FRED API key not provided. Some features may not work.")
            self.fred_client = None
        else:
            self.fred_client = Fred(api_key=self.api_key)

        self.transformer = FREDTransformer()
        self.base_url = "https://api.stlouisfed.org/fred"

    async def get_economic_series(self, series_id: str) -> Dict[str, Any]:
        """Fetch single economic data series from FRED."""
        if not self.fred_client:
            return self._get_mock_data(series_id)

        try:
            loop = asyncio.get_event_loop()

            # Get series data
            series_data = await loop.run_in_executor(
                None, self._fetch_series_data, series_id
            )

            # Get series info
            series_info = await loop.run_in_executor(
                None, self._fetch_series_info, series_id
            )

            return self.transformer.transform_economic_data(
                {
                    "series_data": series_data,
                    "series_info": series_info,
                    "series_id": series_id,
                }
            )

        except Exception as e:
            logger.error(f"Error fetching FRED series {series_id}: {e}")
            return self._get_mock_data(series_id)

    async def get_multiple_series(self, series_ids: List[str]) -> Dict[str, Any]:
        """Fetch multiple economic data series from FRED."""
        result = {}

        if not self.fred_client:
            return {
                series_id: self._get_mock_data(series_id) for series_id in series_ids
            }

        try:
            # Fetch all series concurrently
            tasks = [self.get_economic_series(series_id) for series_id in series_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for series_id, data in zip(series_ids, results):
                if isinstance(data, Exception):
                    logger.error(f"Error fetching {series_id}: {data}")
                    result[series_id] = self._get_mock_data(series_id)
                else:
                    result[series_id] = data

            return result

        except Exception as e:
            logger.error(f"Error fetching multiple FRED series: {e}")
            return {
                series_id: self._get_mock_data(series_id) for series_id in series_ids
            }

    async def get_indicators_by_category(self, category: str) -> Dict[str, Any]:
        """Get all indicators for a specific category."""
        category_series = [
            series_id
            for series_id, info in self.FRED_SERIES_MAPPING.items()
            if info["category"] == category
        ]

        return await self.get_multiple_series(category_series)

    async def get_all_indicators(self) -> Dict[str, Any]:
        """Get all supported economic indicators."""
        all_series = list(self.FRED_SERIES_MAPPING.keys())
        return await self.get_multiple_series(all_series)

    def _fetch_series_data(self, series_id: str):
        """Synchronous helper to fetch series data."""
        # Get data for the last 2 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)

        return self.fred_client.get_series(series_id, start=start_date, end=end_date)

    def _fetch_series_info(self, series_id: str):
        """Synchronous helper to fetch series metadata."""
        return self.fred_client.get_series_info(series_id)

    def _get_mock_data(self, series_id: str) -> Dict[str, Any]:
        """Generate mock data when FRED API is not available."""
        mapping = self.FRED_SERIES_MAPPING.get(series_id, {})

        # Generate realistic mock values based on series type
        mock_values = {
            "DGS2": 4.5,
            "DGS10": 4.8,
            "ICSBULL": 105.2,
            "BAMLH0A0HYM2": 7.8,
            "UNRATE": 3.8,
            "PAYEMS": 156000,
            "AHEPA": 28.50,
            "CPIAUCSL": 295.5,
            "PPIACO": 285.2,
            "T10YIE": 2.3,
            "USACPIALL": 295.8,
            "CLICKSA2": 110.5,
            "M2SL": 21000,
            "FEDFUNDS": 5.25,
            "TEDRATE": 0.35,
            "STLFSI": -0.8,
        }

        return {
            "indicator_code": series_id,
            "name": mapping.get("name", f"Mock {series_id}"),
            "value": mock_values.get(series_id, 100.0),
            "previous_value": mock_values.get(series_id, 100.0) * 0.99,
            "change": mock_values.get(series_id, 100.0) * 0.01,
            "change_percent": 1.0,
            "unit": mapping.get("unit", "Index"),
            "frequency": "monthly",
            "source": "FRED (Mock)",
            "timestamp": datetime.now(),
            "country": "US",
            "category": mapping.get("category", "general"),
        }


class FREDTransformer(DataTransformer):
    """Data transformer for FRED data."""

    def transform_market_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Not used for economic data."""
        return {}

    def transform_economic_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw FRED data to standardized format."""
        try:
            series_data = raw_data["series_data"]
            series_info = raw_data["series_info"]
            series_id = raw_data["series_id"]

            # Get latest value
            if series_data.empty:
                return self._get_empty_indicator(series_id)

            latest_value = float(series_data.iloc[-1])
            previous_value = (
                float(series_data.iloc[-2]) if len(series_data) > 1 else latest_value
            )

            change = latest_value - previous_value
            change_percent = (
                (change / previous_value * 100) if previous_value != 0 else 0
            )

            mapping = FREDProvider.FRED_SERIES_MAPPING.get(series_id, {})

            # Normalize frequency value to match schema requirements
            raw_frequency = series_info.get("frequency", "monthly").lower()
            normalized_frequency = self._normalize_frequency(raw_frequency)

            return {
                "indicator_code": series_id,
                "name": series_info.get("title", mapping.get("name", series_id)),
                "value": latest_value,
                "previous_value": previous_value,
                "change": change,
                "change_percent": change_percent,
                "unit": series_info.get("units", mapping.get("unit", "Index")),
                "frequency": normalized_frequency,
                "source": "FRED",
                "timestamp": datetime.now(),
                "country": "US",
                "category": mapping.get("category", "general"),
                "last_updated": (
                    series_data.index[-1] if not series_data.empty else datetime.now()
                ),
            }

        except Exception as e:
            logger.error(f"Error transforming FRED data: {e}")
            return self._get_empty_indicator(raw_data.get("series_id", "UNKNOWN"))

    def _normalize_frequency(self, raw_frequency: str) -> str:
        """Normalize FRED frequency values to match schema requirements."""
        if not raw_frequency:
            return "monthly"

        frequency_lower = raw_frequency.lower()

        # Map FRED frequency values to schema-compliant values
        if "daily" in frequency_lower:
            return "daily"
        elif "weekly" in frequency_lower:
            return "weekly"
        elif "monthly" in frequency_lower:
            return "monthly"
        elif "quarterly" in frequency_lower:
            return "quarterly"
        elif "annual" in frequency_lower or "yearly" in frequency_lower:
            return "quarterly"  # Map annual to quarterly as closest match
        else:
            # Default fallback
            logger.warning(
                f"Unknown frequency '{raw_frequency}', defaulting to 'monthly'"
            )
            return "monthly"

    def _get_empty_indicator(self, series_id: str) -> Dict[str, Any]:
        """Return empty indicator when data is not available."""
        mapping = FREDProvider.FRED_SERIES_MAPPING.get(series_id, {})

        return {
            "indicator_code": series_id,
            "name": mapping.get("name", f"Data Not Available - {series_id}"),
            "value": 0.0,
            "previous_value": 0.0,
            "change": 0.0,
            "change_percent": 0.0,
            "unit": mapping.get("unit", "Index"),
            "frequency": "monthly",
            "source": "FRED",
            "timestamp": datetime.now(),
            "country": "US",
            "category": mapping.get("category", "general"),
        }
