from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np
from collections import defaultdict

from app.models.portfolio import (
    Portfolio,
    Holding,
    Transaction,
    PortfolioSnapshot,
    DividendPayment,
    PortfolioMetrics,
    TransactionType,
    DividendReinvestmentStrategy,
)
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    TransactionCreate,
    PortfolioSummary,
    PortfolioPerformance,
    DividendAnalysis,
    PortfolioAllocation,
    RiskMetrics,
    ChartData,
    ChartDataPoint,
    PerformanceDataPoint,
    DividendDataPoint,
    AssetAllocation,
)

# TODO: Re-enable when market_data_service is properly implemented
# from app.services.market_data_service import market_data_service


class PortfolioService:
    def __init__(self, db: Session):
        self.db = db

    # Portfolio CRUD Operations
    def create_portfolio(
        self, user_id: str, portfolio_data: PortfolioCreate
    ) -> Portfolio:
        """Create a new portfolio for a user"""
        # Convert string from schema to model's Enum member
        strategy_enum_member = DividendReinvestmentStrategy(
            portfolio_data.dividend_strategy.value
        )

        db_portfolio = Portfolio(
            user_id=user_id,
            name=portfolio_data.name,
            description=portfolio_data.description,
            base_currency=portfolio_data.base_currency,
            dividend_strategy=strategy_enum_member,
        )
        self.db.add(db_portfolio)
        self.db.commit()
        self.db.refresh(db_portfolio)
        return db_portfolio

    def get_portfolios(self, user_id: str) -> List[Portfolio]:
        """Get all portfolios for a user"""
        return self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

    def get_portfolio(self, portfolio_id: int, user_id: str) -> Optional[Portfolio]:
        """Get a specific portfolio"""
        return (
            self.db.query(Portfolio)
            .filter(and_(Portfolio.id == portfolio_id, Portfolio.user_id == user_id))
            .first()
        )

    def update_portfolio(
        self, portfolio_id: int, user_id: str, update_data: PortfolioUpdate
    ) -> Optional[Portfolio]:
        """Update portfolio information"""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return None

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(portfolio, field, value)

        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def delete_portfolio(self, portfolio_id: int, user_id: str) -> bool:
        """Delete a portfolio"""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return False

        self.db.delete(portfolio)
        self.db.commit()
        return True

    # Transaction Operations
    def get_transactions(self, portfolio_id: int, user_id: str) -> List[Transaction]:
        """Get all transactions for a portfolio"""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return []

        return (
            self.db.query(Transaction)
            .filter(Transaction.portfolio_id == portfolio_id)
            .order_by(Transaction.transaction_date.desc())
            .all()
        )

    def add_transaction(
        self, portfolio_id: int, user_id: str, transaction_data: TransactionCreate
    ) -> Optional[Transaction]:
        """Add a transaction to portfolio"""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return None

        # Calculate total amount
        total_amount = (
            transaction_data.quantity * transaction_data.price + transaction_data.fees
        )

        print(
            f"DEBUG: Adding transaction: type={transaction_data.transaction_type}, symbol={transaction_data.symbol}"
        )
        print(
            f"DEBUG: Checking if {transaction_data.transaction_type} in [{TransactionType.buy}, {TransactionType.sell}]"
        )

        # Get or create holding first
        holding_id = None
        if transaction_data.transaction_type in [
            TransactionType.buy,
            TransactionType.sell,
        ]:
            print(f"DEBUG: Calling _update_holding...")
            holding_id = self._update_holding(portfolio_id, transaction_data)
            print(f"DEBUG: Got holding_id={holding_id}")
        else:
            print(
                f"DEBUG: Skipping _update_holding for transaction type: {transaction_data.transaction_type}"
            )

        # Create transaction with holding_id
        db_transaction = Transaction(
            portfolio_id=portfolio_id,
            holding_id=holding_id,
            total_amount=total_amount,
            **transaction_data.dict(),
        )
        self.db.add(db_transaction)

        self.db.commit()
        self.db.refresh(db_transaction)
        print(f"DEBUG: Created transaction with holding_id={db_transaction.holding_id}")
        return db_transaction

    def _update_holding(
        self, portfolio_id: int, transaction_data: TransactionCreate
    ) -> Optional[int]:
        """Update holding based on transaction and return holding ID"""
        print(
            f"DEBUG: _update_holding called for portfolio_id={portfolio_id}, symbol={transaction_data.symbol}"
        )

        holding = (
            self.db.query(Holding)
            .filter(
                and_(
                    Holding.portfolio_id == portfolio_id,
                    Holding.symbol == transaction_data.symbol,
                )
            )
            .first()
        )

        print(f"DEBUG: Found existing holding: {holding is not None}")

        if transaction_data.transaction_type == TransactionType.buy:
            if holding:
                print(f"DEBUG: Updating existing holding with id={holding.id}")
                # Update average cost using weighted average
                total_cost = (holding.quantity * holding.average_cost) + (
                    transaction_data.quantity * transaction_data.price
                )
                new_quantity = holding.quantity + transaction_data.quantity
                holding.average_cost = (
                    total_cost / new_quantity if new_quantity > 0 else 0
                )
                holding.quantity = new_quantity
            else:
                print(
                    f"DEBUG: Creating new holding for symbol={transaction_data.symbol}"
                )
                # Create new holding without external API call for now
                holding = Holding(
                    portfolio_id=portfolio_id,
                    symbol=transaction_data.symbol,
                    quantity=transaction_data.quantity,
                    average_cost=transaction_data.price,
                    company_name=transaction_data.symbol,  # Use symbol as fallback
                    sector="Unknown",  # Default sector
                )
                self.db.add(holding)
                # Flush to get the ID without committing
                self.db.flush()
                print(f"DEBUG: Created new holding with id={holding.id}")

        elif transaction_data.transaction_type == TransactionType.sell and holding:
            print(f"DEBUG: Selling from holding with id={holding.id}")
            holding.quantity = max(0, holding.quantity - transaction_data.quantity)

        result_id = holding.id if holding else None
        print(f"DEBUG: Returning holding_id={result_id}")
        return result_id

    # Portfolio Analysis Methods
    def get_portfolio_summary(
        self, portfolio_id: int, user_id: str
    ) -> Optional[PortfolioSummary]:
        """Get comprehensive portfolio summary"""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return None

        holdings = (
            self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        )
        transactions = (
            self.db.query(Transaction)
            .filter(Transaction.portfolio_id == portfolio_id)
            .order_by(Transaction.transaction_date.desc())
            .limit(10)
            .all()
        )

        # Calculate portfolio metrics
        total_invested = self._calculate_total_invested(portfolio_id)
        total_value = self._calculate_current_portfolio_value(portfolio_id)
        total_dividends = self._calculate_total_dividends(portfolio_id)
        total_return = total_value - total_invested + total_dividends
        return_percentage = (
            (total_return / total_invested * 100) if total_invested > 0 else 0
        )

        return PortfolioSummary(
            portfolio=portfolio,
            total_value=total_value,
            total_invested=total_invested,
            total_return=total_return,
            return_percentage=return_percentage,
            total_dividends=total_dividends,
            holdings_count=len(holdings),
            top_holdings=holdings[:5],  # Top 5 holdings
            recent_transactions=transactions,
        )

    def get_portfolio_performance(
        self,
        portfolio_id: int,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[PortfolioPerformance]:
        """Get portfolio performance over time"""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return None

        if not start_date:
            start_date = portfolio.created_at
        if not end_date:
            end_date = datetime.now(timezone.utc)

        # Get portfolio snapshots or calculate historical values
        snapshots = (
            self.db.query(PortfolioSnapshot)
            .filter(
                and_(
                    PortfolioSnapshot.portfolio_id == portfolio_id,
                    PortfolioSnapshot.snapshot_date >= start_date,
                    PortfolioSnapshot.snapshot_date <= end_date,
                )
            )
            .order_by(PortfolioSnapshot.snapshot_date)
            .all()
        )

        data_points = []

        if snapshots:
            # Use actual snapshot data
            for snapshot in snapshots:
                data_points.append(
                    PerformanceDataPoint(
                        date=snapshot.snapshot_date.isoformat(),
                        portfolio_value=snapshot.total_value,
                        total_invested=snapshot.total_invested,
                        total_return=snapshot.total_return,
                        return_percentage=snapshot.return_percentage,
                        dividends=snapshot.total_dividends,
                    )
                )
        else:
            # Generate mock data for demo purposes
            total_invested = self._calculate_total_invested(portfolio_id)
            current_value = self._calculate_current_portfolio_value(portfolio_id)

            # Generate 6 months of mock data
            current_date = start_date
            months = 0
            while current_date <= end_date and months < 6:
                # Simulate realistic portfolio growth
                growth_factor = 1 + (0.08 * months / 12)  # 8% annual growth
                volatility = (
                    0.03 * (months % 3 - 1) if months > 0 else 0
                )  # Some volatility

                if months == 0:
                    # Start with total invested
                    portfolio_value = total_invested
                    dividends = 0
                else:
                    portfolio_value = total_invested * growth_factor * (1 + volatility)
                    dividends = (
                        total_invested * 0.025 * months / 12
                    )  # 2.5% annual dividend yield

                total_return = portfolio_value - total_invested + dividends
                return_percentage = (
                    (total_return / total_invested * 100) if total_invested > 0 else 0
                )

                data_points.append(
                    PerformanceDataPoint(
                        date=current_date.isoformat(),
                        portfolio_value=portfolio_value,
                        total_invested=total_invested,
                        total_return=total_return,
                        return_percentage=return_percentage,
                        dividends=dividends,
                    )
                )
                current_date += timedelta(days=30)  # Monthly data points
                months += 1

        # Calculate metrics
        metrics = self._calculate_portfolio_metrics(portfolio_id, start_date, end_date)

        return PortfolioPerformance(
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date,
            data_points=data_points,
            metrics=metrics,
        )

    def get_dividend_analysis(
        self, portfolio_id: int, user_id: str
    ) -> Optional[DividendAnalysis]:
        """Get dividend analysis for portfolio"""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return None

        dividends = (
            self.db.query(DividendPayment)
            .filter(DividendPayment.portfolio_id == portfolio_id)
            .order_by(DividendPayment.payment_date)
            .all()
        )

        # Group dividends by month
        monthly_dividends = defaultdict(float)
        cumulative_dividend = 0
        data_points = []

        if dividends:
            # Use actual dividend data
            for dividend in dividends:
                month_key = dividend.payment_date.strftime("%Y-%m")
                monthly_dividends[month_key] += dividend.total_dividend
                cumulative_dividend += dividend.total_dividend

                # Calculate dividend yield (simplified)
                portfolio_value = self._calculate_portfolio_value_at_date(
                    portfolio_id, dividend.payment_date
                )
                dividend_yield = (
                    (dividend.total_dividend / portfolio_value * 100)
                    if portfolio_value > 0
                    else 0
                )

                data_points.append(
                    DividendDataPoint(
                        date=dividend.payment_date.isoformat(),
                        monthly_dividend=monthly_dividends[month_key],
                        cumulative_dividend=cumulative_dividend,
                        dividend_yield=dividend_yield,
                    )
                )
        else:
            # Generate mock dividend data for demo
            portfolio_value = self._calculate_current_portfolio_value(portfolio_id)

            # Generate 6 months of mock dividend data
            for month in range(6):
                date = datetime.now() - timedelta(days=30 * (5 - month))
                monthly_dividend = portfolio_value * 0.02 / 12  # 2% annual yield
                cumulative_dividend += monthly_dividend
                dividend_yield = 2.0  # 2% yield

                data_points.append(
                    DividendDataPoint(
                        date=date.isoformat(),
                        monthly_dividend=monthly_dividend,
                        cumulative_dividend=cumulative_dividend,
                        dividend_yield=dividend_yield,
                    )
                )

        # Calculate metrics
        total_annual_dividend = (
            sum(monthly_dividends.values()) if monthly_dividends else 0
        )
        average_monthly_dividend = (
            total_annual_dividend / 12 if monthly_dividends else 0
        )

        # Calculate dividend growth rate (simplified)
        dividend_growth_rate = self._calculate_dividend_growth_rate(monthly_dividends)

        return DividendAnalysis(
            portfolio_id=portfolio_id,
            total_annual_dividend=total_annual_dividend,
            average_monthly_dividend=average_monthly_dividend,
            dividend_growth_rate=dividend_growth_rate,
            data_points=data_points,
        )

    def get_asset_allocation(
        self, portfolio_id: int, user_id: str
    ) -> Optional[PortfolioAllocation]:
        """Get asset allocation breakdown"""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return None

        holdings = (
            self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        )
        total_value = self._calculate_current_portfolio_value(portfolio_id)

        allocations = []
        sector_breakdown = defaultdict(float)

        for holding in holdings:
            if holding.quantity > 0:
                current_price = self._get_current_price(holding.symbol)
                value = holding.quantity * current_price
                percentage = (value / total_value * 100) if total_value > 0 else 0

                allocation = AssetAllocation(
                    symbol=holding.symbol,
                    company_name=holding.company_name or holding.symbol,
                    sector=holding.sector or "Unknown",
                    value=value,
                    percentage=percentage,
                    dividend_yield=self._get_dividend_yield(holding.symbol),
                )
                allocations.append(allocation)

                # Sector breakdown
                sector_breakdown[holding.sector or "Unknown"] += percentage

        return PortfolioAllocation(
            portfolio_id=portfolio_id,
            total_value=total_value,
            allocations=sorted(allocations, key=lambda x: x.value, reverse=True),
            sector_breakdown=dict(sector_breakdown),
        )

    # Helper Methods for Calculations
    def _calculate_total_invested(self, portfolio_id: int) -> float:
        """Calculate total amount invested"""
        buy_transactions = (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.portfolio_id == portfolio_id,
                    Transaction.transaction_type == TransactionType.buy,
                )
            )
            .all()
        )

        sell_transactions = (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.portfolio_id == portfolio_id,
                    Transaction.transaction_type == TransactionType.sell,
                )
            )
            .all()
        )

        total_bought = sum(t.total_amount for t in buy_transactions)
        total_sold = sum(t.total_amount for t in sell_transactions)

        return total_bought - total_sold

    def _calculate_current_portfolio_value(self, portfolio_id: int) -> float:
        """Calculate current portfolio value"""
        holdings = (
            self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        )
        total_value = 0

        for holding in holdings:
            if holding.quantity > 0:
                current_price = self._get_current_price(holding.symbol)
                total_value += holding.quantity * current_price

        return total_value

    def _calculate_total_dividends(self, portfolio_id: int) -> float:
        """Calculate total dividends received"""
        dividends = (
            self.db.query(DividendPayment)
            .filter(DividendPayment.portfolio_id == portfolio_id)
            .all()
        )

        return sum(d.total_dividend for d in dividends)

    def _calculate_portfolio_value_at_date(
        self, portfolio_id: int, date: datetime
    ) -> float:
        """Calculate portfolio value at specific date"""
        # This would require historical price data
        # For now, return current value as placeholder
        return self._calculate_current_portfolio_value(portfolio_id)

    def _calculate_dividend_growth_rate(
        self, monthly_dividends: Dict[str, float]
    ) -> float:
        """Calculate dividend growth rate"""
        if len(monthly_dividends) < 2:
            return 0.0

        # Simplified calculation - compare first and last year
        months = sorted(monthly_dividends.keys())
        first_year_total = sum(
            monthly_dividends[m] for m in months[:12] if len(months) >= 12
        )
        last_year_total = sum(
            monthly_dividends[m] for m in months[-12:] if len(months) >= 12
        )

        if first_year_total > 0:
            return ((last_year_total / first_year_total) - 1) * 100
        return 0.0

    def _calculate_portfolio_metrics(
        self, portfolio_id: int, start_date: datetime, end_date: datetime
    ) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""
        # Placeholder implementation - would need historical data for proper calculations
        return PortfolioMetrics(
            id=0,
            portfolio_id=portfolio_id,
            metric_date=end_date,
            total_return=0.0,
            annualized_return=0.0,
            volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            dividend_yield=0.0,
            dividend_growth_rate=0.0,
            monthly_dividend=0.0,
            quarterly_dividend=0.0,
            annual_dividend=0.0,
            beta=0.0,
            var_95=0.0,
            var_99=0.0,
            created_at=datetime.now(),
        )

    def _get_current_price(self, symbol: str) -> float:
        """Get current price for symbol - placeholder implementation"""
        # TODO: Implement proper market data service integration
        # For now, return a reasonable mock price based on symbol
        mock_prices = {
            "AAPL": 150.0,
            "GOOGL": 120.0,
            "MSFT": 300.0,
            "TSLA": 200.0,
            "NVDA": 400.0,
            "AMZN": 140.0,
        }
        return mock_prices.get(symbol, 100.0)  # Default price if symbol not found

    def _get_dividend_yield(self, symbol: str) -> Optional[float]:
        """Get dividend yield for symbol - placeholder implementation"""
        # TODO: Implement proper market data service integration
        # For now, return a reasonable mock dividend yield
        mock_yields = {
            "AAPL": 0.5,
            "GOOGL": 0.0,
            "MSFT": 0.7,
            "TSLA": 0.0,
            "NVDA": 0.1,
            "AMZN": 0.0,
        }
        return mock_yields.get(symbol, 0.2)  # Default 0.2% yield

    # Chart Data Generation
    def get_portfolio_value_chart(
        self, portfolio_id: int, user_id: str
    ) -> Optional[ChartData]:
        """Generate portfolio value vs invested chart data"""
        performance = self.get_portfolio_performance(portfolio_id, user_id)
        if not performance:
            return None

        data_points = []
        for point in performance.data_points:
            # Handle both datetime and string date formats
            date_str = (
                point.date.isoformat()
                if hasattr(point.date, "isoformat")
                else str(point.date)
            )

            data_points.append(
                ChartDataPoint(
                    x=date_str,
                    y=point.portfolio_value,
                    label=f"${point.portfolio_value:,.2f}",
                )
            )

        return ChartData(
            chart_type="line",
            title="Portfolio Value Over Time",
            x_axis_label="Date",
            y_axis_label="Value ($)",
            data=data_points,
        )

    def get_dividend_chart(
        self, portfolio_id: int, user_id: str
    ) -> Optional[ChartData]:
        """Get dividend income chart"""
        analysis = self.get_dividend_analysis(portfolio_id, user_id)
        if not analysis:
            return None

        chart_points = [
            ChartDataPoint(
                x=point.date,  # Already formatted string "YYYY-MM"
                y=point.monthly_dividend,
            )
            for point in analysis.data_points
        ]

        return ChartData(
            chart_type="bar",
            title="Monthly Dividend Income",
            x_axis_label="Month",
            y_axis_label="Dividend Amount",
            data=chart_points,
        )
