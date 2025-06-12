from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_sync_db
from app.core.auth import get_current_user, FirebaseUser
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import (
    Portfolio,
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioSummary,
    Transaction,
    TransactionCreate,
    PortfolioPerformance,
    DividendAnalysis,
    PortfolioAllocation,
    ChartData,
)

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])


@router.post("/", response_model=Portfolio, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Create a new portfolio"""
    portfolio_service = PortfolioService(db)
    return portfolio_service.create_portfolio(current_user.uid, portfolio_data)


@router.get("/", response_model=List[Portfolio])
async def get_portfolios(
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Get all portfolios for the current user"""
    portfolio_service = PortfolioService(db)
    return portfolio_service.get_portfolios(current_user.uid)


@router.get("/{portfolio_id}", response_model=Portfolio)
async def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Get a specific portfolio"""
    portfolio_service = PortfolioService(db)
    portfolio = portfolio_service.get_portfolio(portfolio_id, current_user.uid)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    return portfolio


@router.put("/{portfolio_id}", response_model=Portfolio)
async def update_portfolio(
    portfolio_id: int,
    update_data: PortfolioUpdate,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Update a portfolio"""
    portfolio_service = PortfolioService(db)
    portfolio = portfolio_service.update_portfolio(
        portfolio_id, current_user.uid, update_data
    )
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Delete a portfolio"""
    portfolio_service = PortfolioService(db)
    success = portfolio_service.delete_portfolio(portfolio_id, current_user.uid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )


@router.get("/{portfolio_id}/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    portfolio_id: int,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Get comprehensive portfolio summary"""
    portfolio_service = PortfolioService(db)
    summary = portfolio_service.get_portfolio_summary(portfolio_id, current_user.uid)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    return summary


@router.get("/{portfolio_id}/performance", response_model=PortfolioPerformance)
async def get_portfolio_performance(
    portfolio_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Get portfolio performance over time"""
    portfolio_service = PortfolioService(db)
    performance = portfolio_service.get_portfolio_performance(
        portfolio_id, current_user.uid, start_date, end_date
    )
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    return performance


@router.get("/{portfolio_id}/dividends", response_model=DividendAnalysis)
async def get_dividend_analysis(
    portfolio_id: int,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Get dividend analysis for portfolio"""
    portfolio_service = PortfolioService(db)
    analysis = portfolio_service.get_dividend_analysis(portfolio_id, current_user.uid)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    return analysis


@router.get("/{portfolio_id}/allocation", response_model=PortfolioAllocation)
async def get_asset_allocation(
    portfolio_id: int,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Get asset allocation breakdown"""
    portfolio_service = PortfolioService(db)
    allocation = portfolio_service.get_asset_allocation(portfolio_id, current_user.uid)
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    return allocation


# Transaction endpoints
@router.get("/{portfolio_id}/transactions", response_model=List[Transaction])
async def get_transactions(
    portfolio_id: int,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Get all transactions for a portfolio"""
    portfolio_service = PortfolioService(db)
    transactions = portfolio_service.get_transactions(portfolio_id, current_user.uid)
    return transactions


@router.post(
    "/{portfolio_id}/transactions",
    response_model=Transaction,
    status_code=status.HTTP_201_CREATED,
)
async def add_transaction(
    portfolio_id: int,
    transaction_data: TransactionCreate,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Add a transaction to portfolio"""
    portfolio_service = PortfolioService(db)
    transaction = portfolio_service.add_transaction(
        portfolio_id, current_user.uid, transaction_data
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    return transaction


# Chart data endpoints
@router.get("/{portfolio_id}/charts/value", response_model=ChartData)
async def get_portfolio_value_chart(
    portfolio_id: int,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Get portfolio value chart data"""
    portfolio_service = PortfolioService(db)
    chart_data = portfolio_service.get_portfolio_value_chart(
        portfolio_id, current_user.uid
    )
    if not chart_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found or no data available",
        )
    return chart_data


@router.get("/{portfolio_id}/charts/dividends", response_model=ChartData)
async def get_dividend_chart(
    portfolio_id: int,
    db: Session = Depends(get_sync_db),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Get dividend chart data"""
    portfolio_service = PortfolioService(db)
    chart_data = portfolio_service.get_dividend_chart(portfolio_id, current_user.uid)
    if not chart_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found or no data available",
        )
    return chart_data
