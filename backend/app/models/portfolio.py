from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TransactionType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    SPLIT = "SPLIT"


class DividendReinvestmentStrategy(enum.Enum):
    REINVEST = "reinvest"
    CASH = "cash"


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.uid"), index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    base_currency = Column(String(3), default="USD")
    dividend_strategy = Column(
        Enum(DividendReinvestmentStrategy),
        default=DividendReinvestmentStrategy.REINVEST,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship(
        "Holding", back_populates="portfolio", cascade="all, delete-orphan"
    )
    transactions = relationship(
        "Transaction", back_populates="portfolio", cascade="all, delete-orphan"
    )


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    company_name = Column(String(200))
    quantity = Column(Float, nullable=False, default=0.0)
    average_cost = Column(Float, nullable=False, default=0.0)
    sector = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    transactions = relationship("Transaction", back_populates="holding")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    holding_id = Column(Integer, ForeignKey("holdings.id"))
    symbol = Column(String(20), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)  # quantity * price + fees
    fees = Column(Float, default=0.0)
    dividend_per_share = Column(Float)  # For dividend transactions
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    holding = relationship("Holding", back_populates="transactions")


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    snapshot_date = Column(DateTime(timezone=True), nullable=False)
    total_value = Column(Float, nullable=False)
    total_invested = Column(Float, nullable=False)
    total_dividends = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    return_percentage = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DividendPayment(Base):
    __tablename__ = "dividend_payments"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=False)
    ex_dividend_date = Column(DateTime(timezone=True))
    quantity_held = Column(Float, nullable=False)
    dividend_per_share = Column(Float, nullable=False)
    total_dividend = Column(Float, nullable=False)
    is_reinvested = Column(Boolean, default=False)
    reinvested_shares = Column(Float, default=0.0)
    reinvested_price = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PortfolioMetrics(Base):
    __tablename__ = "portfolio_metrics"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    metric_date = Column(DateTime(timezone=True), nullable=False)

    # Performance Metrics
    total_return = Column(Float)
    annualized_return = Column(Float)
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)

    # Dividend Metrics
    dividend_yield = Column(Float)
    dividend_growth_rate = Column(Float)
    monthly_dividend = Column(Float)
    quarterly_dividend = Column(Float)
    annual_dividend = Column(Float)

    # Risk Metrics
    beta = Column(Float)
    var_95 = Column(Float)  # Value at Risk
    var_99 = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
