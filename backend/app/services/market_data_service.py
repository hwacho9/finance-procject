from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import json

from app.services.providers.base import MarketDataProvider, CacheProvider
from app.schemas.market_schemas import (
    MarketIndicesResponse,
    MarketOverviewResponse,
    MarketIndexDetailResponse,
    USMarketIndices,
    EuropeanIndices,
    AsiaPacificIndices,
    MarketIndex,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Service for handling market data operations.
    Follows Single Responsibility Principle - only handles market data logic.
    """

    def __init__(
        self,
        market_provider: MarketDataProvider,
        cache_provider: Optional[CacheProvider] = None,
    ):
        """Dependency injection of providers following DIP."""
        self.market_provider = market_provider
        self.cache_provider = cache_provider

    async def get_indices(self, region: Optional[str] = None) -> MarketIndicesResponse:
        """
        Get market indices data with caching support.

        Args:
            region: Optional region filter (US, EU, ASIA)

        Returns:
            MarketIndicesResponse with indices data
        """
        try:
            # Check cache first
            cache_key = f"market_indices_{region or 'all'}"
            cached_data = await self._get_from_cache(cache_key)

            if cached_data:
                logger.info(f"Returning cached market indices for region: {region}")
                return self._parse_cached_indices(cached_data)

            # Fetch from provider
            logger.info(f"Fetching fresh market indices for region: {region}")
            raw_data = await self.market_provider.get_indices(region)

            # Transform to response model
            response = self._build_indices_response(raw_data, region)

            # Cache the result
            await self._set_cache(cache_key, response.model_dump_json())

            return response

        except Exception as e:
            logger.error(f"Error getting market indices: {e}")
            raise

    async def get_index_detail(
        self, symbol: str, period: str = "1d"
    ) -> MarketIndexDetailResponse:
        """
        Get detailed data for a specific market index.

        Args:
            symbol: Index symbol
            period: Time period for historical data

        Returns:
            MarketIndexDetailResponse with detailed index data
        """
        try:
            cache_key = f"index_detail_{symbol}_{period}"
            cached_data = await self._get_from_cache(cache_key)

            if cached_data:
                logger.info(f"Returning cached index detail for {symbol}")
                return MarketIndexDetailResponse.model_validate_json(cached_data)

            # Fetch current quote
            quote_data = await self.market_provider.get_quote(symbol)

            # Fetch historical data if period is specified
            historical_data = None
            if period != "1d":
                historical_data = await self.market_provider.get_historical_data(
                    symbol, period
                )

            # Build response
            response = MarketIndexDetailResponse(
                index=self._build_market_index(quote_data),
                historical_data=historical_data,
                related_indices=None,  # TODO: Implement related indices logic
            )

            # Cache with shorter TTL for detailed data
            await self._set_cache(
                cache_key, response.model_dump_json(), ttl=300
            )  # 5 minutes

            return response

        except Exception as e:
            logger.error(f"Error getting index detail for {symbol}: {e}")
            raise

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time quote for a specific symbol.

        Args:
            symbol: Index symbol (e.g., SP500, VIX, KOSPI)

        Returns:
            Dict with quote data
        """
        try:
            cache_key = f"quote_{symbol}"
            cached_data = await self._get_from_cache(cache_key)

            if cached_data:
                logger.info(f"Returning cached quote for {symbol}")
                return json.loads(cached_data)

            # Fetch quote from provider
            quote_data = await self.market_provider.get_quote(symbol)

            # Convert datetime to string for JSON serialization
            if "timestamp" in quote_data:
                quote_data["timestamp"] = quote_data["timestamp"].isoformat()

            # Determine cache TTL based on data quality
            # If data looks like mock data (certain patterns), cache for shorter time
            is_likely_mock = self._is_likely_mock_data(quote_data)

            if is_likely_mock:
                cache_ttl = 60  # 1 minute for mock data
                logger.warning(f"Caching likely mock data for {symbol} with short TTL")
            else:
                cache_ttl = 300  # 5 minutes for real data
                logger.info(f"Caching real data for {symbol} with standard TTL")

            # Cache with appropriate TTL
            await self._set_cache(cache_key, json.dumps(quote_data), ttl=cache_ttl)

            return quote_data

        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            raise

    def _is_likely_mock_data(self, quote_data: Dict[str, Any]) -> bool:
        """
        Detect if data is likely mock data based on patterns.

        Args:
            quote_data: Quote data to analyze

        Returns:
            True if data appears to be mock data
        """
        try:
            # Check for common mock data patterns
            current_value = quote_data.get("current_value", 0)
            change_percent = abs(quote_data.get("change_percent", 0))
            volume = quote_data.get("volume", 0)

            # Mock data often has very round numbers or specific ranges
            if current_value == 0:
                return True

            # Check for suspiciously round numbers (often indicates mock data)
            if current_value == int(current_value) and current_value in [
                100,
                1000,
                2000,
                3000,
                4500,
                18000,
                28000,
                35000,
            ]:
                return True

            # Check for volume patterns typical of mock data
            if volume > 0 and (volume % 1000000 == 0 or str(volume).endswith("000000")):
                return True

            # Check for unusually high volatility (typical of mock random data)
            if change_percent > 10:  # >10% daily change is unusual for major indices
                return True

            return False

        except Exception:
            # If we can't analyze, assume it might be mock
            return True

    async def get_market_overview(self) -> MarketOverviewResponse:
        """
        Get comprehensive market overview.

        Returns:
            MarketOverviewResponse with all market data
        """
        try:
            cache_key = "market_overview"
            cached_data = await self._get_from_cache(cache_key)

            if cached_data:
                logger.info("Returning cached market overview")
                return MarketOverviewResponse.model_validate_json(cached_data)

            # Fetch indices data
            indices_response = await self.get_indices()

            # TODO: Add bonds, volatility, commodities, currencies
            # For now, just return indices
            response = MarketOverviewResponse(
                indices=indices_response,
                bonds=None,
                volatility=None,
                commodities=None,
                currencies=None,
                last_updated=datetime.now(),
            )

            # Cache with standard TTL
            await self._set_cache(cache_key, response.model_dump_json())

            return response

        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            raise

    async def refresh_cache(self, region: Optional[str] = None) -> bool:
        """
        Force refresh of cached market data.

        Args:
            region: Optional region to refresh

        Returns:
            True if successful
        """
        try:
            cache_key = f"market_indices_{region or 'all'}"

            # Delete existing cache
            if self.cache_provider:
                await self.cache_provider.delete(cache_key)

            # Fetch fresh data
            await self.get_indices(region)

            logger.info(f"Successfully refreshed cache for region: {region}")
            return True

        except Exception as e:
            logger.error(f"Error refreshing cache: {e}")
            return False

    def _build_indices_response(
        self, raw_data: Dict[str, Any], region: Optional[str]
    ) -> MarketIndicesResponse:
        """Build MarketIndicesResponse from raw provider data."""

        # Separate data by region
        us_data = {}
        eu_data = {}
        asia_data = {}

        for symbol, data in raw_data.items():
            if symbol in ["DJIA", "SP500", "NASDAQ", "RUSSELL2000", "PHLX_SOX"]:
                us_data[symbol] = data
            elif symbol in ["EURO_STOXX50", "FTSE100", "DAX", "CAC40", "IBEX35"]:
                eu_data[symbol] = data
            elif symbol in [
                "NIKKEI225",
                "TOPIX",
                "SHANGHAI_COMPOSITE",
                "HANG_SENG",
                "KOSPI",
                "KOSDAQ",
                "ASX200",
            ]:
                asia_data[symbol] = data

        # Build US indices (required)
        us_indices = self._build_us_indices(us_data)

        # Build optional regional indices
        european_indices = self._build_european_indices(eu_data) if eu_data else None
        asia_pacific_indices = (
            self._build_asia_pacific_indices(asia_data) if asia_data else None
        )

        return MarketIndicesResponse(
            us_indices=us_indices,
            european_indices=european_indices,
            asia_pacific_indices=asia_pacific_indices,
            timestamp=datetime.now(),
        )

    def _build_us_indices(self, data: Dict[str, Any]) -> USMarketIndices:
        """Build US indices from data."""
        return USMarketIndices(
            djia=self._build_market_index(data.get("DJIA", {})),
            sp500=self._build_market_index(data.get("SP500", {})),
            nasdaq=self._build_market_index(data.get("NASDAQ", {})),
            russell2000=self._build_market_index(data.get("RUSSELL2000", {})),
            phlx_sox=(
                self._build_market_index(data.get("PHLX_SOX"))
                if "PHLX_SOX" in data
                else None
            ),
        )

    def _build_european_indices(self, data: Dict[str, Any]) -> EuropeanIndices:
        """Build European indices from data."""
        return EuropeanIndices(
            euro_stoxx50=self._build_market_index(data.get("EURO_STOXX50", {})),
            ftse100=self._build_market_index(data.get("FTSE100", {})),
            dax=self._build_market_index(data.get("DAX", {})),
            cac40=self._build_market_index(data.get("CAC40", {})),
            ibex35=(
                self._build_market_index(data.get("IBEX35"))
                if "IBEX35" in data
                else None
            ),
        )

    def _build_asia_pacific_indices(self, data: Dict[str, Any]) -> AsiaPacificIndices:
        """Build Asia-Pacific indices from data."""
        return AsiaPacificIndices(
            nikkei225=self._build_market_index(data.get("NIKKEI225", {})),
            topix=(
                self._build_market_index(data.get("TOPIX")) if "TOPIX" in data else None
            ),
            shanghai_composite=self._build_market_index(
                data.get("SHANGHAI_COMPOSITE", {})
            ),
            hang_seng=self._build_market_index(data.get("HANG_SENG", {})),
            kospi=self._build_market_index(data.get("KOSPI", {})),
            kosdaq=(
                self._build_market_index(data.get("KOSDAQ"))
                if "KOSDAQ" in data
                else None
            ),
            asx200=(
                self._build_market_index(data.get("ASX200"))
                if "ASX200" in data
                else None
            ),
        )

    def _build_market_index(self, data: Dict[str, Any]) -> MarketIndex:
        """Build MarketIndex from provider data."""
        if not data:
            # Return placeholder data if no data available
            return MarketIndex(
                symbol="N/A",
                name="Data Not Available",
                current_value=0.0,
                change=0.0,
                change_percent=0.0,
                timestamp=datetime.now(),
                market_status="closed",
            )

        return MarketIndex(
            symbol=data.get("symbol", "N/A"),
            name=data.get("name", "Unknown"),
            current_value=data.get("current_value", 0.0),
            change=data.get("change", 0.0),
            change_percent=data.get("change_percent", 0.0),
            timestamp=data.get("timestamp", datetime.now()),
            market_status=data.get("market_status", "closed"),
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
            cache_ttl = ttl or settings.market_data_cache_ttl
            await self.cache_provider.set(key, value, cache_ttl)
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")

    def _parse_cached_indices(self, cached_data: str) -> MarketIndicesResponse:
        """Parse cached indices data."""
        try:
            return MarketIndicesResponse.model_validate_json(cached_data)
        except Exception as e:
            logger.warning(f"Error parsing cached indices data: {e}")
            raise


# Factory function for creating MarketDataService with proper dependencies
def create_market_data_service() -> MarketDataService:
    """
    Factory function to create MarketDataService with dependencies.
    Follows Dependency Injection pattern.
    """
    from app.services.providers.alpha_vantage import AlphaVantageProvider

    market_provider = AlphaVantageProvider()
    # For now, create without cache provider to avoid FastAPI dependency issues
    return MarketDataService(market_provider, None)
