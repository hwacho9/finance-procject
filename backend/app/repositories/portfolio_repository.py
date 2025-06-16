from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime

from app.models.portfolio import (
    Portfolio,
    Holding,
    Transaction,
    PortfolioSnapshot,
    DividendPayment,
    PortfolioMetrics,
    TransactionType,
)
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    TransactionCreate,
)
from app.repositories.base_repository import BaseRepository


class PortfolioRepository(BaseRepository[Portfolio, PortfolioCreate, PortfolioUpdate]):
    """Portfolio repository with specific business logic"""

    def __init__(self, db: Session):
        super().__init__(db, Portfolio)

    def get_by_user(self, user_id: str) -> List[Portfolio]:
        """Get all portfolios for a specific user"""
        return self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

    def get_by_user_and_id(
        self, user_id: str, portfolio_id: int
    ) -> Optional[Portfolio]:
        """Get a specific portfolio for a user"""
        return (
            self.db.query(Portfolio)
            .filter(and_(Portfolio.id == portfolio_id, Portfolio.user_id == user_id))
            .first()
        )


class HoldingRepository(BaseRepository[Holding, dict, dict]):
    """Holding repository with specific business logic"""

    def __init__(self, db: Session):
        super().__init__(db, Holding)

    def get_by_portfolio(self, portfolio_id: int) -> List[Holding]:
        """Get all holdings for a portfolio"""
        return self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()

    def get_by_portfolio_and_symbol(
        self, portfolio_id: int, symbol: str
    ) -> Optional[Holding]:
        """Get holding by portfolio and symbol"""
        return (
            self.db.query(Holding)
            .filter(
                and_(
                    Holding.portfolio_id == portfolio_id,
                    Holding.symbol == symbol,
                )
            )
            .first()
        )

    def get_active_holdings(self, portfolio_id: int) -> List[Holding]:
        """Get active holdings (quantity > 0) for a portfolio"""
        return (
            self.db.query(Holding)
            .filter(and_(Holding.portfolio_id == portfolio_id, Holding.quantity > 0))
            .all()
        )

    def create_or_update_holding(
        self,
        portfolio_id: int,
        symbol: str,
        quantity_change: float,
        price: float,
        transaction_type: TransactionType,
    ) -> Holding:
        """Create new holding or update existing one based on transaction"""
        holding = self.get_by_portfolio_and_symbol(portfolio_id, symbol)

        if transaction_type == TransactionType.buy:
            if holding:
                print(f"DEBUG: Updating existing holding with id={holding.id}")
                # Update existing holding with weighted average cost
                total_cost = (holding.quantity * holding.average_cost) + (
                    quantity_change * price
                )
                new_quantity = holding.quantity + quantity_change
                holding.average_cost = (
                    total_cost / new_quantity if new_quantity > 0 else 0
                )
                holding.quantity = new_quantity
                self.db.commit()
                self.db.refresh(holding)
            else:
                print(f"DEBUG: Creating new holding for symbol={symbol}")
                # Create new holding without external API call for now
                holding = Holding(
                    portfolio_id=portfolio_id,
                    symbol=symbol,
                    quantity=quantity_change,
                    average_cost=price,
                    company_name=symbol,  # Use symbol as fallback
                    sector="Unknown",  # Default sector
                )
                self.db.add(holding)
                # Flush to get the ID without committing
                self.db.flush()
                print(f"DEBUG: Created new holding with id={holding.id}")

        elif transaction_type == TransactionType.sell:
            if holding:
                print(f"DEBUG: Selling from holding with id={holding.id}")
                holding.quantity = max(0, holding.quantity - quantity_change)
                self.db.commit()
                self.db.refresh(holding)
            else:
                raise ValueError("No holding found to sell")

        return holding


class TransactionRepository(BaseRepository[Transaction, dict, dict]):
    """Transaction repository with specific business logic"""

    def __init__(self, db: Session):
        super().__init__(db, Transaction)

    def create_transaction(self, transaction_data: dict) -> Transaction:
        """Create a new transaction"""
        db_transaction = Transaction(**transaction_data)
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def get_by_portfolio(
        self, portfolio_id: int, limit: int = 100, offset: int = 0
    ) -> List[Transaction]:
        """Get transactions for a portfolio with pagination"""
        return (
            self.db.query(Transaction)
            .filter(Transaction.portfolio_id == portfolio_id)
            .order_by(Transaction.transaction_date.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_symbol(self, portfolio_id: int, symbol: str) -> List[Transaction]:
        """Get all transactions for a specific symbol in a portfolio"""
        return (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.portfolio_id == portfolio_id,
                    Transaction.symbol == symbol,
                )
            )
            .order_by(Transaction.transaction_date.desc())
            .all()
        )

    def get_buy_transactions(self, portfolio_id: int) -> List[Transaction]:
        """Get all buy transactions for a portfolio"""
        return (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.portfolio_id == portfolio_id,
                    Transaction.transaction_type == TransactionType.buy,
                )
            )
            .all()
        )

    def get_sell_transactions(self, portfolio_id: int) -> List[Transaction]:
        """Get all sell transactions for a portfolio"""
        return (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.portfolio_id == portfolio_id,
                    Transaction.transaction_type == TransactionType.sell,
                )
            )
            .all()
        )

    def get_dividend_transactions(self, portfolio_id: int) -> List[Transaction]:
        """Get all dividend transactions for a portfolio"""
        return (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.portfolio_id == portfolio_id,
                    Transaction.transaction_type == TransactionType.dividend,
                )
            )
            .all()
        )

    def calculate_total_invested(self, portfolio_id: int) -> float:
        """Calculate total amount invested (buy transactions - sell transactions)"""
        buy_total = (
            self.db.query(func.sum(Transaction.total_amount))
            .filter(
                and_(
                    Transaction.portfolio_id == portfolio_id,
                    Transaction.transaction_type == TransactionType.buy,
                )
            )
            .scalar()
            or 0
        )

        sell_total = (
            self.db.query(func.sum(Transaction.total_amount))
            .filter(
                and_(
                    Transaction.portfolio_id == portfolio_id,
                    Transaction.transaction_type == TransactionType.sell,
                )
            )
            .scalar()
            or 0
        )

        return buy_total - sell_total

    def calculate_total_dividends(self, portfolio_id: int) -> float:
        """Calculate total dividends received"""
        return (
            self.db.query(func.sum(Transaction.total_amount))
            .filter(
                and_(
                    Transaction.portfolio_id == portfolio_id,
                    Transaction.transaction_type == TransactionType.dividend,
                )
            )
            .scalar()
            or 0
        )


class DividendPaymentRepository(BaseRepository[DividendPayment, dict, dict]):
    """Dividend payment repository"""

    def __init__(self, db: Session):
        super().__init__(db, DividendPayment)

    def get_by_portfolio(self, portfolio_id: int) -> List[DividendPayment]:
        """Get all dividend payments for a portfolio"""
        return (
            self.db.query(DividendPayment)
            .filter(DividendPayment.portfolio_id == portfolio_id)
            .order_by(DividendPayment.payment_date.desc())
            .all()
        )
