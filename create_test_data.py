#!/usr/bin/env python3

import sys
import os

sys.path.append("/app")

from app.core.database import get_sync_session
from app.models.portfolio import Portfolio, Transaction, Holding, TransactionType
from datetime import datetime, date
import uuid


def create_test_data():
    # 세션 생성
    session = next(get_sync_session())

    try:
        # 기존 데이터 삭제
        session.query(Holding).delete()
        session.query(Transaction).delete()
        session.query(Portfolio).delete()
        session.commit()

        # 테스트용 포트폴리오 생성
        portfolio = Portfolio(
            id=1,
            user_id="test-user",
            name="내 포트폴리오",
            description="테스트용 포트폴리오",
            base_currency="USD",
        )

        session.add(portfolio)
        session.commit()

        # 테스트용 거래 데이터 생성
        transactions = [
            Transaction(
                portfolio_id=1,
                symbol="AAPL",
                transaction_type=TransactionType.BUY,
                quantity=10,
                price=150.0,
                total_amount=1505.0,  # quantity * price + fees
                fees=5.0,
                transaction_date=datetime(2024, 1, 15),
                notes="Initial AAPL purchase",
            ),
            Transaction(
                portfolio_id=1,
                symbol="MSFT",
                transaction_type=TransactionType.BUY,
                quantity=5,
                price=300.0,
                total_amount=1505.0,  # quantity * price + fees
                fees=5.0,
                transaction_date=datetime(2024, 2, 10),
                notes="Initial MSFT purchase",
            ),
            Transaction(
                portfolio_id=1,
                symbol="GOOGL",
                transaction_type=TransactionType.BUY,
                quantity=3,
                price=120.0,
                total_amount=365.0,  # quantity * price + fees
                fees=5.0,
                transaction_date=datetime(2024, 3, 5),
                notes="Initial GOOGL purchase",
            ),
        ]

        for transaction in transactions:
            session.add(transaction)

        session.commit()

        # 테스트용 보유 종목 생성
        holdings = [
            Holding(
                portfolio_id=1,
                symbol="AAPL",
                company_name="Apple Inc.",
                quantity=10,
                average_cost=150.0,
                sector="Technology",
            ),
            Holding(
                portfolio_id=1,
                symbol="MSFT",
                company_name="Microsoft Corporation",
                quantity=5,
                average_cost=300.0,
                sector="Technology",
            ),
            Holding(
                portfolio_id=1,
                symbol="GOOGL",
                company_name="Alphabet Inc.",
                quantity=3,
                average_cost=120.0,
                sector="Technology",
            ),
        ]

        for holding in holdings:
            session.add(holding)

        session.commit()
        print("Test portfolio data created successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error creating test data: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    create_test_data()
