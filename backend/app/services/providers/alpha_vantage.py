import requests
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import time

from app.services.providers.base import MarketDataProvider, DataTransformer
from app.core.config import settings

logger = logging.getLogger(__name__)


class AlphaVantageProvider(MarketDataProvider):
    """Alpha Vantage implementation of MarketDataProvider."""

    # Mapping of our standardized symbols to Alpha Vantage symbols
    SYMBOL_MAPPING = {
        # US Indices (ETFs that track indices)
        "DJIA": "DIA",  # SPDR Dow Jones Industrial Average ETF
        "SP500": "SPY",  # SPDR S&P 500 ETF Trust
        "NASDAQ": "QQQ",  # Invesco QQQ Trust (NASDAQ-100)
        "RUSsell2000": "IWM",  # iShares Russell 2000 ETF
        "PHLX_SOX": "SOXX",  # iShares Semiconductor ETF
        # Volatility
        "VIX": "VXX",  # iPath S&P 500 VIX Short-Term Futures ETN
        # Major stocks as proxies for regional indices
        "NIKKEI225": "EWJ",  # iShares MSCI Japan ETF
        "HANG_SENG": "EWH",  # iShares MSCI Hong Kong ETF
        "KOSPI": "EWY",  # iShares MSCI South Korea ETF
        # European indices
        "EURO_STOXX50": "EXS4.DE",  # Euro Stoxx 50
        "FTSE100": "ISF.L",  # iShares Core FTSE 100 UCITS ETF
        "DAX": "EXS1.DE",  # Euro Stoxx 50
        # Commodities
        "GOLD": "GLD",  # SPDR Gold Trust
        "SILVER": "SLV",  # iShares Silver Trust
        "WTI_CRUDE": "USO",  # United States Oil Fund
        # Currencies
        "EUR_USD": "FXE",  # Invesco CurrencyShares Euro Trust
        "USD_JPY": "FXY",  # Invesco CurrencyShares Japanese Yen Trust
        "DXY": "UUP",  # Invesco DB US Dollar Index Bullish Fund
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.alpha_vantage_api_key
        self.transformer = AlphaVantageTransformer()
        self.base_url = "https://www.alphavantage.co/query"
        self.request_delay = 12.0  # Alpha Vantage free tier: 5 requests per minute
        self.last_request_time = 0

        if not self.api_key:
            logger.warning(
                "Alpha Vantage API key not configured. Using demo key (limited functionality)"
            )
            self.api_key = "demo"

    async def get_indices(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Fetch market indices data."""
        try:
            # Select symbols based on region
            if region == "US":
                symbols = ["DJIA", "SP500", "NASDAQ", "RUSsell2000", "PHLX_SOX"]
            elif region == "EU":
                symbols = ["EURO_STOXX50", "FTSE100", "DAX"]
            elif region == "ASIA":
                symbols = ["NIKKEI225", "HANG_SENG", "KOSPI"]
            else:
                # Default: get major indices from all regions
                symbols = ["DJIA", "SP500", "NASDAQ", "NIKKEI225", "HANG_SENG", "KOSPI"]

            # Fetch data for each symbol
            loop = asyncio.get_event_loop()
            raw_data = await loop.run_in_executor(
                None, self._fetch_multiple_quotes, symbols
            )

            return self.transformer.transform_market_data(raw_data)

        except Exception as e:
            logger.error(f"Error fetching indices data: {e}")
            raise

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for specific symbol."""
        try:
            alpha_symbol = self.SYMBOL_MAPPING.get(symbol, symbol)

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, self._fetch_single_quote, alpha_symbol
            )

            return self.transformer.transform_quote_data(data, symbol)

        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            raise

    async def get_historical_data(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """Get historical data for symbol."""
        try:
            alpha_symbol = self.SYMBOL_MAPPING.get(symbol, symbol)

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, self._fetch_historical_data, alpha_symbol
            )

            return self.transformer.transform_historical_data(data, symbol)

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            raise

    def _wait_for_rate_limit(self):
        """Ensure we don't exceed Alpha Vantage rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            logger.info(
                f"Alpha Vantage rate limiting: waiting {sleep_time:.1f} seconds"
            )
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _fetch_single_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch single quote from Alpha Vantage."""
        try:
            self._wait_for_rate_limit()

            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key,
            }

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Debug: Log the full response to understand what Alpha Vantage is returning
            logger.info(f"Alpha Vantage response for {symbol}: {data}")

            # Check for API errors
            if "Error Message" in data:
                raise Exception(f"Alpha Vantage API Error: {data['Error Message']}")

            if "Note" in data:
                raise Exception(f"Alpha Vantage API Limit: {data['Note']}")

            # Extract quote data
            quote_data = data.get("Global Quote", {})

            if not quote_data:
                logger.warning(
                    f"Empty quote data from Alpha Vantage for {symbol}. Full response: {data}"
                )
                raise Exception(f"No quote data returned for {symbol}")

            logger.info(f"Successfully fetched Alpha Vantage data for {symbol}")
            return quote_data

        except Exception as e:
            logger.error(f"Failed to fetch Alpha Vantage data for {symbol}: {e}")
            raise

    def _fetch_multiple_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch multiple quotes from Alpha Vantage."""
        result = {}

        for symbol in symbols:
            try:
                alpha_symbol = self.SYMBOL_MAPPING.get(symbol, symbol)
                quote_data = self._fetch_single_quote(alpha_symbol)
                result[symbol] = quote_data
            except Exception as e:
                logger.warning(f"Failed to fetch data for {symbol}: {e}")
                # Continue with other symbols
                continue

        return result

    def _fetch_historical_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch historical data from Alpha Vantage."""
        try:
            self._wait_for_rate_limit()

            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": self.api_key,
            }

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                raise Exception(f"Alpha Vantage API Error: {data['Error Message']}")

            if "Note" in data:
                raise Exception(f"Alpha Vantage API Limit: {data['Note']}")

            return data

        except Exception as e:
            logger.error(f"Failed to fetch historical data for {symbol}: {e}")
            raise


class AlphaVantageTransformer(DataTransformer):
    """Data transformer for Alpha Vantage data."""

    def transform_market_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw Alpha Vantage data to standardized format."""
        transformed = {}

        for symbol, data in raw_data.items():
            if not data:
                continue

            try:
                transformed[symbol] = self._transform_quote_to_standard(data, symbol)
            except Exception as e:
                logger.warning(f"Error transforming data for {symbol}: {e}")
                continue

        return transformed

    def transform_economic_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform economic data (not applicable for Alpha Vantage stock data)."""
        return {}

    def transform_quote_data(
        self, raw_data: Dict[str, Any], symbol: str
    ) -> Dict[str, Any]:
        """Transform single quote data."""
        return self._transform_quote_to_standard(raw_data, symbol)

    def transform_historical_data(
        self, raw_data: Dict[str, Any], symbol: str
    ) -> List[Dict[str, Any]]:
        """Transform historical data."""
        try:
            time_series = raw_data.get("Time Series (Daily)", {})

            result = []
            for date, values in time_series.items():
                result.append(
                    {
                        "date": date,
                        "symbol": symbol,
                        "open": float(values.get("1. open", 0)),
                        "high": float(values.get("2. high", 0)),
                        "low": float(values.get("3. low", 0)),
                        "close": float(values.get("4. close", 0)),
                        "volume": int(values.get("5. volume", 0)),
                    }
                )

            # Sort by date (most recent first)
            result.sort(key=lambda x: x["date"], reverse=True)
            return result[:30]  # Return last 30 days

        except Exception as e:
            logger.error(f"Error transforming historical data for {symbol}: {e}")
            return []

    def _transform_quote_to_standard(
        self, raw_data: Dict[str, Any], symbol: str
    ) -> Dict[str, Any]:
        """Transform Alpha Vantage quote data to standard format."""
        try:
            # Alpha Vantage Global Quote format
            current_price = float(raw_data.get("05. price", 0))
            change = float(raw_data.get("09. change", 0))
            change_percent = raw_data.get("10. change percent", "0%").replace("%", "")
            change_percent = float(change_percent) if change_percent else 0

            # Determine market status based on trading day
            latest_trading_day = raw_data.get("07. latest trading day", "")
            today = datetime.now().strftime("%Y-%m-%d")
            market_status = "open" if latest_trading_day == today else "closed"

            return {
                "symbol": symbol,
                "name": raw_data.get("01. symbol", symbol),
                "current_value": current_price,
                "change": change,
                "change_percent": change_percent,
                "timestamp": datetime.now(),
                "market_status": market_status,
                "volume": int(raw_data.get("06. volume", 0)),
                "market_cap": None,
                "high": float(raw_data.get("03. high", 0)),
                "low": float(raw_data.get("04. low", 0)),
                "open": float(raw_data.get("02. open", 0)),
                "previous_close": float(raw_data.get("08. previous close", 0)),
            }

        except Exception as e:
            logger.error(f"Error transforming quote data for {symbol}: {e}")
            raise
