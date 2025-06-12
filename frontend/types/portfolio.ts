// Portfolio Types
export interface Portfolio {
    id: number;
    user_id: string;
    name: string;
    description?: string;
    base_currency: string;
    dividend_strategy: DividendReinvestmentStrategy;
    created_at: string;
    updated_at?: string;
}

export interface PortfolioCreate {
    name: string;
    description?: string;
    base_currency?: string;
    dividend_strategy?: DividendReinvestmentStrategy;
}

export interface PortfolioUpdate {
    name?: string;
    description?: string;
    dividend_strategy?: DividendReinvestmentStrategy;
}

export enum TransactionType {
    BUY = "buy",
    SELL = "sell",
    DIVIDEND = "dividend",
    SPLIT = "split",
}

export enum DividendReinvestmentStrategy {
    REINVEST = "reinvest",
    CASH = "cash",
}

// Transaction Types
export interface Transaction {
    id: number;
    portfolio_id: number;
    holding_id?: number;
    symbol: string;
    transaction_type: TransactionType;
    quantity: number;
    price: number;
    total_amount: number;
    fees: number;
    dividend_per_share?: number;
    transaction_date: string;
    notes?: string;
    created_at: string;
}

export interface TransactionCreate {
    symbol: string;
    transaction_type: TransactionType;
    quantity: number;
    price: number;
    fees?: number;
    dividend_per_share?: number;
    transaction_date: string;
    notes?: string;
}

// Holding Types
export interface Holding {
    id: number;
    portfolio_id: number;
    symbol: string;
    company_name?: string;
    sector?: string;
    quantity: number;
    average_cost: number;
    current_price?: number;
    current_value?: number;
    unrealized_gain_loss?: number;
    unrealized_gain_loss_percent?: number;
    created_at: string;
    updated_at?: string;
}

// Portfolio Summary
export interface PortfolioSummary {
    portfolio: Portfolio;
    total_value: number;
    total_invested: number;
    total_return: number;
    return_percentage: number;
    total_dividends: number;
    holdings_count: number;
    top_holdings: Holding[];
    recent_transactions: Transaction[];
}

// Performance Types
export interface PerformanceDataPoint {
    date: string;
    portfolio_value: number;
    total_invested: number;
    total_return: number;
    return_percentage: number;
    dividends: number;
}

export interface PortfolioPerformance {
    portfolio_id: number;
    start_date: string;
    end_date: string;
    data_points: PerformanceDataPoint[];
    metrics: PortfolioMetrics;
}

export interface PortfolioMetrics {
    id: number;
    portfolio_id: number;
    metric_date: string;
    total_return?: number;
    annualized_return?: number;
    volatility?: number;
    sharpe_ratio?: number;
    max_drawdown?: number;
    dividend_yield?: number;
    dividend_growth_rate?: number;
    monthly_dividend?: number;
    quarterly_dividend?: number;
    annual_dividend?: number;
    beta?: number;
    var_95?: number;
    var_99?: number;
    created_at: string;
}

// Dividend Types
export interface DividendDataPoint {
    date: string;
    monthly_dividend: number;
    cumulative_dividend: number;
    dividend_yield: number;
}

export interface DividendAnalysis {
    portfolio_id: number;
    total_annual_dividend: number;
    average_monthly_dividend: number;
    dividend_growth_rate: number;
    data_points: DividendDataPoint[];
}

// Asset Allocation Types
export interface AssetAllocation {
    symbol: string;
    company_name: string;
    sector: string;
    value: number;
    percentage: number;
    dividend_yield?: number;
}

export interface PortfolioAllocation {
    portfolio_id: number;
    total_value: number;
    allocations: AssetAllocation[];
    sector_breakdown: Record<string, number>;
}

// Chart Types
export interface ChartDataPoint {
    x: string | number | Date;
    y: number;
    label?: string;
}

export interface ChartData {
    chart_type: string;
    title: string;
    x_axis_label: string;
    y_axis_label: string;
    data: ChartDataPoint[];
    metadata?: Record<string, unknown>;
}

// Risk Analysis Types
export interface RiskMetrics {
    portfolio_id: number;
    calculation_date: string;
    volatility: number;
    max_drawdown: number;
    sharpe_ratio: number;
    beta: number;
    var_95: number;
    var_99: number;
    correlation_matrix?: Record<string, Record<string, number>>;
}
