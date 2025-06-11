from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class MarketIndex(BaseModel):
    """Base schema for market index data."""

    symbol: str = Field(..., description="Index symbol (e.g., ^GSPC for S&P 500)")
    name: str = Field(..., description="Full name of the index")
    current_value: float = Field(..., description="Current index value")
    change: float = Field(..., description="Point change from previous close")
    change_percent: float = Field(
        ..., description="Percentage change from previous close"
    )
    timestamp: datetime = Field(..., description="Last update timestamp")
    market_status: Literal["open", "closed", "pre-market", "after-hours"] = Field(
        ..., description="Current market status"
    )


class YieldData(BaseModel):
    """Treasury yield data schema."""

    rate: float = Field(..., description="Current yield rate")
    change: float = Field(..., description="Change from previous session")
    timestamp: datetime = Field(..., description="Data timestamp")


class VolatilityIndex(BaseModel):
    """Volatility index schema."""

    symbol: str = Field(..., description="Volatility index symbol")
    value: float = Field(..., description="Current volatility value")
    change: float = Field(..., description="Change from previous session")
    level: Literal["low", "medium", "high", "extreme"] = Field(
        ..., description="Volatility level classification"
    )
    timestamp: datetime = Field(..., description="Data timestamp")


class CommodityPrice(BaseModel):
    """Commodity price schema."""

    symbol: str = Field(..., description="Commodity symbol")
    name: str = Field(..., description="Commodity name")
    price: float = Field(..., description="Current price")
    change: float = Field(..., description="Price change")
    change_percent: float = Field(..., description="Percentage change")
    unit: str = Field(..., description="Price unit (e.g., USD/barrel)")
    timestamp: datetime = Field(..., description="Data timestamp")


class CurrencyPair(BaseModel):
    """Currency pair schema."""

    pair: str = Field(..., description="Currency pair (e.g., EUR/USD)")
    rate: float = Field(..., description="Exchange rate")
    change: float = Field(..., description="Rate change")
    change_percent: float = Field(..., description="Percentage change")
    timestamp: datetime = Field(..., description="Data timestamp")


# Regional Index Collections
class USMarketIndices(BaseModel):
    """US major market indices."""

    djia: MarketIndex = Field(..., description="Dow Jones Industrial Average")
    sp500: MarketIndex = Field(..., description="S&P 500")
    nasdaq: MarketIndex = Field(..., description="NASDAQ Composite")
    russell2000: MarketIndex = Field(..., description="Russell 2000")
    phlx_sox: Optional[MarketIndex] = Field(
        None, description="Philadelphia Semiconductor Index"
    )


class EuropeanIndices(BaseModel):
    """European major market indices."""

    euro_stoxx50: MarketIndex = Field(..., description="Euro Stoxx 50")
    ftse100: MarketIndex = Field(..., description="FTSE 100")
    dax: MarketIndex = Field(..., description="DAX")
    cac40: MarketIndex = Field(..., description="CAC 40")
    ibex35: Optional[MarketIndex] = Field(None, description="IBEX 35")


class AsiaPacificIndices(BaseModel):
    """Asia-Pacific major market indices."""

    nikkei225: MarketIndex = Field(..., description="Nikkei 225")
    topix: Optional[MarketIndex] = Field(None, description="TOPIX")
    shanghai_composite: MarketIndex = Field(..., description="Shanghai Composite")
    hang_seng: MarketIndex = Field(..., description="Hang Seng")
    kospi: MarketIndex = Field(..., description="KOSPI")
    kosdaq: Optional[MarketIndex] = Field(None, description="KOSDAQ")
    asx200: Optional[MarketIndex] = Field(None, description="S&P/ASX 200")


class BondYieldData(BaseModel):
    """Bond and treasury yield data."""

    year2: YieldData = Field(..., description="2-Year Treasury")
    year5: YieldData = Field(..., description="5-Year Treasury")
    year10: YieldData = Field(..., description="10-Year Treasury")
    year30: YieldData = Field(..., description="30-Year Treasury")


class VolatilityIndices(BaseModel):
    """Volatility indices collection."""

    cboe_vix: VolatilityIndex = Field(..., description="CBOE VIX")
    vxn: Optional[VolatilityIndex] = Field(None, description="NASDAQ Volatility")
    vstoxx: Optional[VolatilityIndex] = Field(None, description="European Volatility")
    vkospi: Optional[VolatilityIndex] = Field(None, description="Korean Volatility")


class CommodityData(BaseModel):
    """Commodity data collection."""

    wti_crude: CommodityPrice = Field(..., description="WTI Crude Oil")
    brent_crude: CommodityPrice = Field(..., description="Brent Crude Oil")
    natural_gas: Optional[CommodityPrice] = Field(None, description="Natural Gas")
    gold: CommodityPrice = Field(..., description="Gold Spot Price")
    silver: Optional[CommodityPrice] = Field(None, description="Silver")
    copper: Optional[CommodityPrice] = Field(None, description="Copper")


class CurrencyData(BaseModel):
    """Currency data collection."""

    eur_usd: CurrencyPair = Field(..., description="EUR/USD")
    usd_jpy: CurrencyPair = Field(..., description="USD/JPY")
    gbp_usd: CurrencyPair = Field(..., description="GBP/USD")
    dxy: Optional[CurrencyPair] = Field(None, description="US Dollar Index")


# Main Response Models
class MarketIndicesResponse(BaseModel):
    """Complete market indices response."""

    us_indices: USMarketIndices
    european_indices: Optional[EuropeanIndices] = None
    asia_pacific_indices: Optional[AsiaPacificIndices] = None
    timestamp: datetime = Field(..., description="Response timestamp")


class MarketOverviewResponse(BaseModel):
    """Complete market overview response."""

    indices: MarketIndicesResponse
    bonds: Optional[BondYieldData] = None
    volatility: Optional[VolatilityIndices] = None
    commodities: Optional[CommodityData] = None
    currencies: Optional[CurrencyData] = None
    last_updated: datetime = Field(..., description="Last data update time")


class MarketIndexDetailResponse(BaseModel):
    """Detailed response for a specific market index."""

    index: MarketIndex
    historical_data: Optional[List[dict]] = Field(
        None, description="Historical price data"
    )
    related_indices: Optional[List[MarketIndex]] = Field(
        None, description="Related indices"
    )
