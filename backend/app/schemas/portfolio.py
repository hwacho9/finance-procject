from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Import TransactionType and DividendReinvestmentStrategy from models
from app.models.portfolio import TransactionType, DividendReinvestmentStrategy


# Portfolio Schemas
class PortfolioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    base_currency: str = Field(default="USD", max_length=3)
    dividend_strategy: DividendReinvestmentStrategy = (
        DividendReinvestmentStrategy.REINVEST
    )


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    dividend_strategy: Optional[DividendReinvestmentStrategy] = None


class Portfolio(PortfolioBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionBase(BaseModel):
    symbol: str = Field(..., max_length=20)
    transaction_type: TransactionType
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    fees: float = Field(default=0.0, ge=0)
    dividend_per_share: Optional[float] = Field(None, ge=0)
    transaction_date: datetime
    notes: Optional[str] = None

    @validator("transaction_date", pre=True)
    def parse_transaction_date(cls, value):
        if isinstance(value, str):
            # Handle both date format (YYYY-MM-DD) and datetime format
            try:
                if "T" in value:
                    # ISO datetime format
                    return datetime.fromisoformat(value.replace("Z", "+00:00"))
                else:
                    # Date format - assume start of day
                    return datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    "Invalid date format. Use YYYY-MM-DD or ISO datetime format"
                )
        return value


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: int
    portfolio_id: int
    holding_id: Optional[int] = None
    total_amount: float
    created_at: datetime

    class Config:
        from_attributes = True


# Holding Schemas
class HoldingBase(BaseModel):
    symbol: str = Field(..., max_length=20)
    company_name: Optional[str] = Field(None, max_length=200)
    sector: Optional[str] = Field(None, max_length=100)


class Holding(HoldingBase):
    id: int
    portfolio_id: int
    quantity: float
    average_cost: float
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    unrealized_gain_loss: Optional[float] = None
    unrealized_gain_loss_percent: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Portfolio Metrics Schemas
class PortfolioMetricsBase(BaseModel):
    total_return: Optional[float] = None
    annualized_return: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    dividend_yield: Optional[float] = None
    dividend_growth_rate: Optional[float] = None
    monthly_dividend: Optional[float] = None
    quarterly_dividend: Optional[float] = None
    annual_dividend: Optional[float] = None
    beta: Optional[float] = None
    var_95: Optional[float] = None
    var_99: Optional[float] = None


class PortfolioMetrics(PortfolioMetricsBase):
    id: int
    portfolio_id: int
    metric_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Portfolio Summary Schemas
class PortfolioSummary(BaseModel):
    portfolio: Portfolio
    total_value: float
    total_invested: float
    total_return: float
    return_percentage: float
    total_dividends: float
    holdings_count: int
    top_holdings: List[Holding]
    recent_transactions: List[Transaction]


# Portfolio Performance Schemas
class PerformanceDataPoint(BaseModel):
    date: str  # ISO format date string
    portfolio_value: float
    total_invested: float
    total_return: float
    return_percentage: float
    dividends: float


class PortfolioPerformance(BaseModel):
    portfolio_id: int
    start_date: datetime
    end_date: datetime
    data_points: List[PerformanceDataPoint]
    metrics: PortfolioMetrics


# Dividend Analysis Schemas
class DividendDataPoint(BaseModel):
    date: str  # ISO format date string
    monthly_dividend: float
    cumulative_dividend: float
    dividend_yield: float


class DividendAnalysis(BaseModel):
    portfolio_id: int
    total_annual_dividend: float
    average_monthly_dividend: float
    dividend_growth_rate: float
    data_points: List[DividendDataPoint]


# Asset Allocation Schemas
class AssetAllocation(BaseModel):
    symbol: str
    company_name: str
    sector: str
    value: float
    percentage: float
    dividend_yield: Optional[float] = None


class PortfolioAllocation(BaseModel):
    portfolio_id: int
    total_value: float
    allocations: List[AssetAllocation]
    sector_breakdown: Dict[str, float]


# Risk Analysis Schemas
class RiskMetrics(BaseModel):
    portfolio_id: int
    calculation_date: datetime
    volatility: float
    max_drawdown: float
    sharpe_ratio: float
    beta: float
    var_95: float
    var_99: float
    correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None


# Chart Data Schemas
class ChartDataPoint(BaseModel):
    x: Any  # Can be date, string, number
    y: float
    label: Optional[str] = None


class ChartData(BaseModel):
    chart_type: str  # line, bar, area, etc.
    title: str
    x_axis_label: str
    y_axis_label: str
    data: List[ChartDataPoint]
    metadata: Optional[Dict[str, Any]] = None
