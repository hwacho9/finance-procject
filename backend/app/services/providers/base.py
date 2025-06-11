from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class MarketDataProvider(ABC):
    """Abstract base class for market data providers."""

    @abstractmethod
    async def get_indices(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Fetch market indices data."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for specific symbol."""
        pass

    @abstractmethod
    async def get_historical_data(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """Get historical data for symbol."""
        pass


class EconomicDataProvider(ABC):
    """Abstract base class for economic data providers."""

    @abstractmethod
    async def get_economic_series(self, series_id: str) -> Dict[str, Any]:
        """Fetch economic data series."""
        pass

    @abstractmethod
    async def get_multiple_series(self, series_ids: List[str]) -> Dict[str, Any]:
        """Fetch multiple economic data series."""
        pass


class CommodityDataProvider(ABC):
    """Abstract base class for commodity data providers."""

    @abstractmethod
    async def get_commodity_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch commodity prices."""
        pass


class CurrencyDataProvider(ABC):
    """Abstract base class for currency data providers."""

    @abstractmethod
    async def get_exchange_rates(self, pairs: List[str]) -> Dict[str, Any]:
        """Fetch exchange rates."""
        pass


class VolatilityDataProvider(ABC):
    """Abstract base class for volatility data providers."""

    @abstractmethod
    async def get_volatility_indices(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch volatility indices."""
        pass


class DataTransformer(ABC):
    """Abstract base class for data transformation."""

    @abstractmethod
    def transform_market_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw market data to standardized format."""
        pass

    @abstractmethod
    def transform_economic_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw economic data to standardized format."""
        pass


class CacheProvider(ABC):
    """Abstract base class for caching providers."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get cached data."""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int) -> None:
        """Set cached data with TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete cached data."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
