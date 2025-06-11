from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class EconomicIndicator(BaseModel):
    """Base schema for economic indicators."""

    indicator_code: str = Field(..., description="Unique indicator code")
    name: str = Field(..., description="Full name of the indicator")
    value: float = Field(..., description="Current indicator value")
    previous_value: Optional[float] = Field(None, description="Previous period value")
    change: Optional[float] = Field(None, description="Change from previous period")
    change_percent: Optional[float] = Field(None, description="Percentage change")
    unit: str = Field(..., description="Unit of measurement")
    frequency: Literal["daily", "weekly", "monthly", "quarterly"] = Field(
        ..., description="Data frequency"
    )
    source: str = Field(..., description="Data source")
    timestamp: datetime = Field(..., description="Data timestamp")
    country: str = Field(default="US", description="Country code")


class PMIData(BaseModel):
    """PMI (Purchasing Managers' Index) data."""

    manufacturing: EconomicIndicator = Field(..., description="Manufacturing PMI")
    services: EconomicIndicator = Field(..., description="Services PMI")
    composite: Optional[EconomicIndicator] = Field(None, description="Composite PMI")


class InflationData(BaseModel):
    """Inflation indicators."""

    headline: EconomicIndicator = Field(..., description="Headline inflation")
    core: EconomicIndicator = Field(
        ..., description="Core inflation (ex food & energy)"
    )
    month_over_month: Optional[float] = Field(
        None, description="Month-over-month change"
    )
    year_over_year: Optional[float] = Field(None, description="Year-over-year change")


class EmploymentData(BaseModel):
    """Employment indicators."""

    unemployment_rate: EconomicIndicator = Field(..., description="Unemployment rate")
    nonfarm_payrolls: EconomicIndicator = Field(
        ..., description="Nonfarm payrolls change"
    )
    average_hourly_earnings: EconomicIndicator = Field(
        ..., description="Average hourly earnings"
    )
    labor_force_participation: Optional[EconomicIndicator] = Field(
        None, description="Labor force participation rate"
    )


class HousingData(BaseModel):
    """Housing market indicators."""

    housing_starts: EconomicIndicator = Field(..., description="Housing starts")
    existing_home_sales: EconomicIndicator = Field(
        ..., description="Existing home sales"
    )
    new_home_sales: Optional[EconomicIndicator] = Field(
        None, description="New home sales"
    )
    home_price_index: Optional[EconomicIndicator] = Field(
        None, description="Home price index"
    )


class ConsumerSentimentData(BaseModel):
    """Consumer sentiment indicators."""

    consumer_confidence: EconomicIndicator = Field(
        ..., description="Consumer confidence index"
    )
    consumer_expectations: EconomicIndicator = Field(
        ..., description="Consumer expectations"
    )
    current_conditions: Optional[EconomicIndicator] = Field(
        None, description="Current economic conditions"
    )


class BusinessSentimentData(BaseModel):
    """Business sentiment indicators."""

    business_confidence: EconomicIndicator = Field(
        ..., description="Business confidence index"
    )
    small_business_optimism: Optional[EconomicIndicator] = Field(
        None, description="Small business optimism index"
    )


class MonetaryData(BaseModel):
    """Monetary policy indicators."""

    fed_funds_rate: EconomicIndicator = Field(..., description="Federal funds rate")
    m2_money_supply: EconomicIndicator = Field(..., description="M2 money supply")
    ted_spread: Optional[EconomicIndicator] = Field(None, description="TED spread")
    sofr: Optional[EconomicIndicator] = Field(None, description="SOFR rate")


class FinancialStabilityData(BaseModel):
    """Financial stability indicators."""

    yield_curve_slope: EconomicIndicator = Field(
        ..., description="Yield curve slope (10Y-2Y)"
    )
    financial_stress_index: EconomicIndicator = Field(
        ..., description="Financial stress index"
    )
    credit_spread: Optional[EconomicIndicator] = Field(
        None, description="Corporate credit spread"
    )


class LeadingIndicators(BaseModel):
    """Leading economic indicators."""

    lei_oecd: EconomicIndicator = Field(..., description="OECD Leading Economic Index")
    lei_conference_board: EconomicIndicator = Field(
        ..., description="Conference Board LEI"
    )


# Regional Economic Data
class USEconomicData(BaseModel):
    """US economic indicators collection."""

    leading_indicators: LeadingIndicators
    pmi: PMIData
    inflation: InflationData
    employment: EmploymentData
    housing: HousingData
    consumer_sentiment: ConsumerSentimentData
    business_sentiment: Optional[BusinessSentimentData] = None
    monetary: MonetaryData
    financial_stability: FinancialStabilityData


class GlobalEconomicData(BaseModel):
    """Global economic indicators collection."""

    us: USEconomicData
    # Future: Add EU, China, Japan, etc.


# Response Models
class EconomicIndicatorsResponse(BaseModel):
    """Economic indicators API response."""

    data: GlobalEconomicData
    last_updated: datetime = Field(..., description="Last data update time")
    source_info: Optional[dict] = Field(None, description="Data source information")


class EconomicIndicatorDetailResponse(BaseModel):
    """Detailed response for a specific economic indicator."""

    indicator: EconomicIndicator
    historical_data: Optional[List[dict]] = Field(
        None, description="Historical data points"
    )
    forecast: Optional[List[dict]] = Field(
        None, description="Forecast data if available"
    )
    related_indicators: Optional[List[EconomicIndicator]] = Field(
        None, description="Related economic indicators"
    )


class EconomicSummaryResponse(BaseModel):
    """Economic summary response."""

    key_indicators: List[EconomicIndicator] = Field(
        ..., description="Key economic indicators"
    )
    trends: Optional[List[dict]] = Field(None, description="Economic trend analysis")
    alerts: Optional[List[dict]] = Field(
        None, description="Economic alerts or warnings"
    )
    last_updated: datetime = Field(..., description="Last update timestamp")
