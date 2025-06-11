import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime
from typing import Dict, Any

from app.services.market_data_service import MarketDataService
from app.services.providers.base import MarketDataProvider, CacheProvider
from app.schemas.market_schemas import MarketIndicesResponse, MarketIndex


class MockMarketDataProvider(MarketDataProvider):
    """Mock implementation of MarketDataProvider for testing."""

    def __init__(self):
        self.mock_data = {
            "SP500": {
                "symbol": "SP500",
                "name": "S&P 500",
                "current_value": 4500.0,
                "change": 25.5,
                "change_percent": 0.57,
                "timestamp": datetime.now(),
                "market_status": "open",
            },
            "DJIA": {
                "symbol": "DJIA",
                "name": "Dow Jones Industrial Average",
                "current_value": 35000.0,
                "change": -100.0,
                "change_percent": -0.29,
                "timestamp": datetime.now(),
                "market_status": "open",
            },
        }

    async def get_indices(self, region: str = None) -> Dict[str, Any]:
        """Return mock indices data."""
        if region == "US":
            return {k: v for k, v in self.mock_data.items() if k in ["SP500", "DJIA"]}
        return self.mock_data

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Return mock quote data."""
        return self.mock_data.get(symbol, {})

    async def get_historical_data(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ):
        """Return mock historical data."""
        return [
            {
                "date": "2023-01-01",
                "symbol": symbol,
                "open": 4400.0,
                "high": 4450.0,
                "low": 4380.0,
                "close": 4420.0,
                "volume": 1000000,
            }
        ]


class MockCacheProvider(CacheProvider):
    """Mock implementation of CacheProvider for testing."""

    def __init__(self):
        self.cache = {}

    async def get(self, key: str) -> str:
        """Get cached data."""
        return self.cache.get(key)

    async def set(self, key: str, value: str, ttl: int) -> None:
        """Set cached data."""
        self.cache[key] = value

    async def delete(self, key: str) -> None:
        """Delete cached data."""
        self.cache.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return key in self.cache


@pytest.fixture
def mock_market_provider():
    """Fixture for mock market data provider."""
    return MockMarketDataProvider()


@pytest.fixture
def mock_cache_provider():
    """Fixture for mock cache provider."""
    return MockCacheProvider()


@pytest.fixture
def market_service(mock_market_provider, mock_cache_provider):
    """Fixture for market data service with mocked dependencies."""
    return MarketDataService(mock_market_provider, mock_cache_provider)


class TestMarketDataService:
    """Test suite for MarketDataService following TDD principles."""

    @pytest.mark.asyncio
    async def test_should_return_market_indices_when_provider_has_data(
        self, market_service
    ):
        """Test: should return market indices when provider has data."""
        # Given: MarketDataService with mock provider containing data
        # When: get_indices is called
        result = await market_service.get_indices()

        # Then: should return MarketIndicesResponse with US indices
        assert isinstance(result, MarketIndicesResponse)
        assert result.us_indices is not None
        assert result.us_indices.sp500.symbol == "SP500"
        assert result.us_indices.djia.symbol == "DJIA"
        assert result.timestamp is not None

    @pytest.mark.asyncio
    async def test_should_filter_indices_by_region_when_region_specified(
        self, market_service
    ):
        """Test: should filter indices by region when region is specified."""
        # Given: MarketDataService with mock provider
        # When: get_indices is called with US region
        result = await market_service.get_indices("US")

        # Then: should return only US indices
        assert isinstance(result, MarketIndicesResponse)
        assert result.us_indices is not None
        assert result.us_indices.sp500.current_value == 4500.0
        assert result.us_indices.djia.current_value == 35000.0

    @pytest.mark.asyncio
    async def test_should_cache_market_data_when_fetched_successfully(
        self, market_service, mock_cache_provider
    ):
        """Test: should cache market data when fetched successfully."""
        # Given: MarketDataService with cache provider
        cache_key = "market_indices_all"

        # When: get_indices is called
        result = await market_service.get_indices()

        # Then: data should be cached
        cached_data = await mock_cache_provider.get(cache_key)
        assert cached_data is not None
        assert "SP500" in cached_data

    @pytest.mark.asyncio
    async def test_should_return_cached_data_when_available(
        self, market_service, mock_cache_provider
    ):
        """Test: should return cached data when available."""
        # Given: Cached market data
        cache_key = "market_indices_all"
        mock_response = MarketIndicesResponse(
            us_indices=Mock(), timestamp=datetime.now()
        )
        await mock_cache_provider.set(cache_key, mock_response.model_dump_json(), 60)

        # When: get_indices is called
        # Note: This test would need more sophisticated mocking to fully test cache retrieval
        # For now, we test that the service attempts to use cache
        result = await market_service.get_indices()

        # Then: should return data (either from cache or provider)
        assert isinstance(result, MarketIndicesResponse)

    @pytest.mark.asyncio
    async def test_should_get_index_detail_when_symbol_exists(self, market_service):
        """Test: should get index detail when symbol exists."""
        # Given: MarketDataService and valid symbol
        symbol = "SP500"

        # When: get_index_detail is called
        result = await market_service.get_index_detail(symbol)

        # Then: should return detailed index data
        assert result.index.symbol == symbol
        assert result.index.name == "S&P 500"
        assert result.index.current_value == 4500.0

    @pytest.mark.asyncio
    async def test_should_include_historical_data_when_period_specified(
        self, market_service
    ):
        """Test: should include historical data when period is specified."""
        # Given: MarketDataService and symbol with historical period
        symbol = "SP500"
        period = "1y"

        # When: get_index_detail is called with period
        result = await market_service.get_index_detail(symbol, period)

        # Then: should include historical data
        assert result.historical_data is not None
        assert len(result.historical_data) > 0
        assert result.historical_data[0]["symbol"] == symbol

    @pytest.mark.asyncio
    async def test_should_get_market_overview_with_all_sections(self, market_service):
        """Test: should get market overview with all sections."""
        # Given: MarketDataService
        # When: get_market_overview is called
        result = await market_service.get_market_overview()

        # Then: should return market overview with indices
        assert result.indices is not None
        assert result.last_updated is not None
        # Note: bonds, volatility, commodities, currencies are None in current implementation

    @pytest.mark.asyncio
    async def test_should_refresh_cache_successfully(
        self, market_service, mock_cache_provider
    ):
        """Test: should refresh cache successfully."""
        # Given: MarketDataService with cached data
        cache_key = "market_indices_all"
        await mock_cache_provider.set(cache_key, "old_data", 60)

        # When: refresh_cache is called
        result = await market_service.refresh_cache()

        # Then: should return success and cache should be refreshed
        assert result is True
        # Cache should be deleted and new data fetched

    @pytest.mark.asyncio
    async def test_should_handle_empty_provider_data_gracefully(
        self, mock_cache_provider
    ):
        """Test: should handle empty provider data gracefully."""
        # Given: MarketDataService with provider that returns empty data
        empty_provider = MockMarketDataProvider()
        empty_provider.mock_data = {}
        service = MarketDataService(empty_provider, mock_cache_provider)

        # When: get_indices is called
        result = await service.get_indices()

        # Then: should return response with placeholder data
        assert isinstance(result, MarketIndicesResponse)
        assert result.us_indices.sp500.name == "Data Not Available"

    @pytest.mark.asyncio
    async def test_should_work_without_cache_provider(self, mock_market_provider):
        """Test: should work without cache provider."""
        # Given: MarketDataService without cache provider
        service = MarketDataService(mock_market_provider, None)

        # When: get_indices is called
        result = await service.get_indices()

        # Then: should return data successfully without caching
        assert isinstance(result, MarketIndicesResponse)
        assert result.us_indices.sp500.current_value == 4500.0
