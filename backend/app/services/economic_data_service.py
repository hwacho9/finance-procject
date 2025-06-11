from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from app.services.providers.base import EconomicDataProvider, CacheProvider
from app.services.providers.fred_provider import FREDProvider
from app.schemas.economic_schemas import (
    EconomicIndicator,
    EconomicIndicatorsResponse,
    EconomicIndicatorDetailResponse,
    USEconomicData,
    GlobalEconomicData,
    PMIData,
    InflationData,
    EmploymentData,
    HousingData,
    ConsumerSentimentData,
    BusinessSentimentData,
    MonetaryData,
    FinancialStabilityData,
    LeadingIndicators,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class EconomicDataService:
    """
    Service for handling economic data operations.
    Follows Single Responsibility Principle - only handles economic data logic.
    """

    def __init__(
        self,
        economic_provider: EconomicDataProvider,
        cache_provider: Optional[CacheProvider] = None,
    ):
        """Dependency injection of providers following DIP."""
        self.economic_provider = economic_provider
        self.cache_provider = cache_provider

    async def get_all_indicators(self) -> EconomicIndicatorsResponse:
        """Get all economic indicators."""
        try:
            # Check cache first
            cache_key = "economic_indicators_all"
            cached_data = await self._get_from_cache(cache_key)

            if cached_data:
                logger.info("Returning cached economic indicators")
                return EconomicIndicatorsResponse.model_validate_json(cached_data)

            # Fetch from provider
            logger.info("Fetching fresh economic indicators")
            raw_data = await self.economic_provider.get_all_indicators()

            # Transform to response model
            response = self._build_indicators_response(raw_data)

            # Cache the result
            await self._set_cache(cache_key, response.model_dump_json())

            return response

        except Exception as e:
            logger.error(f"Error getting economic indicators: {e}")
            raise

    async def get_indicators_by_category(self, category: str) -> Dict[str, Any]:
        """Get economic indicators by category."""
        try:
            cache_key = f"economic_indicators_{category}"
            cached_data = await self._get_from_cache(cache_key)

            if cached_data:
                logger.info(
                    f"Returning cached economic indicators for category: {category}"
                )
                return cached_data

            # Fetch from provider
            logger.info(f"Fetching fresh economic indicators for category: {category}")
            raw_data = await self.economic_provider.get_indicators_by_category(category)

            # Cache the result
            await self._set_cache(cache_key, raw_data, ttl=1800)  # 30 minutes

            return raw_data

        except Exception as e:
            logger.error(f"Error getting indicators for category {category}: {e}")
            raise

    async def get_indicator_detail(
        self, indicator_code: str
    ) -> EconomicIndicatorDetailResponse:
        """Get detailed data for a specific economic indicator."""
        try:
            cache_key = f"economic_indicator_{indicator_code}"
            cached_data = await self._get_from_cache(cache_key)

            if cached_data:
                logger.info(f"Returning cached indicator detail for {indicator_code}")
                return EconomicIndicatorDetailResponse.model_validate_json(cached_data)

            # Fetch current data
            indicator_data = await self.economic_provider.get_economic_series(
                indicator_code
            )

            # Build response
            response = EconomicIndicatorDetailResponse(
                indicator=self._build_economic_indicator(indicator_data),
                historical_data=None,  # TODO: Implement historical data
                forecast=None,  # TODO: Implement forecast data
                related_indicators=None,  # TODO: Implement related indicators
            )

            # Cache with shorter TTL for detailed data
            await self._set_cache(
                cache_key, response.model_dump_json(), ttl=900
            )  # 15 minutes

            return response

        except Exception as e:
            logger.error(f"Error getting indicator detail for {indicator_code}: {e}")
            raise

    async def get_bonds_data(self) -> Dict[str, Any]:
        """Get bond-related economic indicators."""
        return await self.get_indicators_by_category("bonds")

    async def get_employment_data(self) -> Dict[str, Any]:
        """Get employment-related economic indicators."""
        return await self.get_indicators_by_category("employment")

    async def get_inflation_data(self) -> Dict[str, Any]:
        """Get inflation-related economic indicators."""
        return await self.get_indicators_by_category("inflation")

    async def get_monetary_data(self) -> Dict[str, Any]:
        """Get monetary policy indicators."""
        return await self.get_indicators_by_category("monetary")

    async def get_financial_stability_data(self) -> Dict[str, Any]:
        """Get financial stability indicators."""
        return await self.get_indicators_by_category("financial_stability")

    async def refresh_cache(self, category: Optional[str] = None) -> bool:
        """Force refresh of cached economic data."""
        try:
            if category:
                cache_key = f"economic_indicators_{category}"
                # Delete existing cache
                if self.cache_provider:
                    await self.cache_provider.delete(cache_key)
                # Fetch fresh data
                await self.get_indicators_by_category(category)
            else:
                cache_key = "economic_indicators_all"
                # Delete existing cache
                if self.cache_provider:
                    await self.cache_provider.delete(cache_key)
                # Fetch fresh data
                await self.get_all_indicators()

            logger.info(
                f"Successfully refreshed cache for category: {category or 'all'}"
            )
            return True

        except Exception as e:
            logger.error(f"Error refreshing cache: {e}")
            return False

    def _build_indicators_response(
        self, raw_data: Dict[str, Any]
    ) -> EconomicIndicatorsResponse:
        """Build EconomicIndicatorsResponse from raw provider data."""

        # 카테고리별로 데이터 분류
        bonds_data = {k: v for k, v in raw_data.items() if v.get("category") == "bonds"}
        employment_data = {
            k: v for k, v in raw_data.items() if v.get("category") == "employment"
        }
        inflation_data = {
            k: v for k, v in raw_data.items() if v.get("category") == "inflation"
        }
        monetary_data = {
            k: v for k, v in raw_data.items() if v.get("category") == "monetary"
        }
        financial_data = {
            k: v
            for k, v in raw_data.items()
            if v.get("category") == "financial_stability"
        }
        leading_data = {
            k: v
            for k, v in raw_data.items()
            if v.get("category") == "leading_indicators"
        }

        try:
            # Build US economic data structure
            us_data = USEconomicData(
                leading_indicators=LeadingIndicators(
                    lei_oecd=self._build_economic_indicator(
                        leading_data.get("CLICKSA2", {})
                    ),
                    lei_conference_board=self._build_economic_indicator(
                        leading_data.get("CLICKSA2", {})
                    ),
                ),
                pmi=PMIData(
                    manufacturing=self._build_placeholder_indicator(
                        "Manufacturing PMI"
                    ),
                    services=self._build_placeholder_indicator("Services PMI"),
                ),
                inflation=InflationData(
                    headline=self._build_economic_indicator(
                        inflation_data.get("CPIAUCSL", {})
                    ),
                    core=self._build_economic_indicator(
                        inflation_data.get("USACPIALL", {})
                    ),
                ),
                employment=EmploymentData(
                    unemployment_rate=self._build_economic_indicator(
                        employment_data.get("UNRATE", {})
                    ),
                    nonfarm_payrolls=self._build_economic_indicator(
                        employment_data.get("PAYEMS", {})
                    ),
                    average_hourly_earnings=self._build_economic_indicator(
                        employment_data.get("AHEPA", {})
                    ),
                ),
                housing=HousingData(
                    housing_starts=self._build_placeholder_indicator("Housing Starts"),
                    existing_home_sales=self._build_placeholder_indicator(
                        "Existing Home Sales"
                    ),
                ),
                consumer_sentiment=ConsumerSentimentData(
                    consumer_confidence=self._build_placeholder_indicator(
                        "Consumer Confidence"
                    ),
                    consumer_expectations=self._build_placeholder_indicator(
                        "Consumer Expectations"
                    ),
                ),
                monetary=MonetaryData(
                    fed_funds_rate=self._build_economic_indicator(
                        monetary_data.get("FEDFUNDS", {})
                    ),
                    m2_money_supply=self._build_economic_indicator(
                        monetary_data.get("M2SL", {})
                    ),
                    ted_spread=self._build_economic_indicator(
                        financial_data.get("TEDRATE", {})
                    ),
                ),
                financial_stability=FinancialStabilityData(
                    yield_curve_slope=self._build_placeholder_indicator(
                        "Yield Curve Slope"
                    ),
                    financial_stress_index=self._build_economic_indicator(
                        financial_data.get("STLFSI", {})
                    ),
                ),
            )

            global_data = GlobalEconomicData(us=us_data)

            return EconomicIndicatorsResponse(
                data=global_data,
                last_updated=datetime.now(),
                source_info={
                    "provider": "FRED",
                    "indicators_count": len(raw_data),
                    "categories": list(
                        set(v.get("category", "general") for v in raw_data.values())
                    ),
                },
            )

        except Exception as e:
            logger.error(f"Error building indicators response: {e}")
            raise

    def _build_economic_indicator(self, data: Dict[str, Any]) -> EconomicIndicator:
        """Build EconomicIndicator from provider data."""
        if not data:
            return self._build_placeholder_indicator("Data Not Available")

        return EconomicIndicator(
            indicator_code=data.get("indicator_code", "N/A"),
            name=data.get("name", "Unknown"),
            value=data.get("value", 0.0),
            previous_value=data.get("previous_value"),
            change=data.get("change"),
            change_percent=data.get("change_percent"),
            unit=data.get("unit", "Index"),
            frequency=data.get("frequency", "monthly"),
            source=data.get("source", "FRED"),
            timestamp=data.get("timestamp", datetime.now()),
            country=data.get("country", "US"),
        )

    def _build_placeholder_indicator(self, name: str) -> EconomicIndicator:
        """Build placeholder indicator when data is not available."""
        return EconomicIndicator(
            indicator_code="N/A",
            name=name,
            value=0.0,
            unit="Index",
            frequency="monthly",
            source="Placeholder",
            timestamp=datetime.now(),
            country="US",
        )

    async def _get_from_cache(self, key: str) -> Optional[str]:
        """Get data from cache if available."""
        if not self.cache_provider:
            return None

        try:
            return await self.cache_provider.get(key)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None

    async def _set_cache(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set data in cache."""
        if not self.cache_provider:
            return

        try:
            cache_ttl = ttl or settings.economic_data_cache_ttl
            await self.cache_provider.set(key, value, cache_ttl)
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")


# Factory function for creating EconomicDataService with proper dependencies
def create_economic_data_service() -> EconomicDataService:
    """
    Factory function to create EconomicDataService with dependencies.
    Follows Dependency Injection pattern.
    """
    economic_provider = FREDProvider()
    # For now, create without cache provider to avoid FastAPI dependency issues
    return EconomicDataService(economic_provider, None)
