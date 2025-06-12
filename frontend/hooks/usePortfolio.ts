import { useState, useEffect } from "react";
import { portfolioAPI } from "@/lib/api/portfolio";
import {
    PortfolioSummary,
    TransactionCreate,
    Transaction,
    PerformanceDataPoint,
    DividendDataPoint,
    AssetAllocation,
} from "@/types/portfolio";

interface UsePortfolioState {
    summary: PortfolioSummary | null;
    performanceData: PerformanceDataPoint[];
    dividendData: DividendDataPoint[];
    allocationData: AssetAllocation[];
    transactions: Transaction[];
    loading: boolean;
    error: string | null;
}

export const usePortfolio = (portfolioId: number | null) => {
    const [state, setState] = useState<UsePortfolioState>({
        summary: null,
        performanceData: [],
        dividendData: [],
        allocationData: [],
        transactions: [],
        loading: true,
        error: null,
    });

    const fetchPortfolioData = async (id: number) => {
        try {
            setState((prev) => ({ ...prev, loading: true, error: null }));

            const [
                summary,
                performanceData,
                dividendData,
                allocationData,
                transactions,
            ] = await Promise.all([
                portfolioAPI.getPortfolioSummary(id),
                portfolioAPI.getPerformanceData(id),
                portfolioAPI.getDividendData(id),
                portfolioAPI.getAssetAllocation(id),
                portfolioAPI.getTransactions(id),
            ]);

            setState({
                summary,
                performanceData,
                dividendData,
                allocationData,
                transactions,
                loading: false,
                error: null,
            });
        } catch (error) {
            console.error("Failed to fetch portfolio data:", error);
            setState((prev) => ({
                ...prev,
                loading: false,
                error:
                    error instanceof Error
                        ? error.message
                        : "Failed to fetch data",
            }));
        }
    };

    const addTransaction = async (transaction: TransactionCreate) => {
        if (!portfolioId) {
            throw new Error("Portfolio ID is not available.");
        }
        try {
            const newTransaction = await portfolioAPI.addTransaction(
                portfolioId,
                transaction
            );
            setState((prev) => ({
                ...prev,
                transactions: [...prev.transactions, newTransaction],
            }));

            // Refresh portfolio data after adding transaction
            await fetchPortfolioData(portfolioId);

            return newTransaction;
        } catch (error) {
            console.error("Failed to add transaction:", error);
            throw error;
        }
    };

    const refetch = () => {
        if (portfolioId) {
            fetchPortfolioData(portfolioId);
        }
    };

    useEffect(() => {
        if (portfolioId) {
            fetchPortfolioData(portfolioId);
        } else {
            // Clear data if portfolioId is null
            setState({
                summary: null,
                performanceData: [],
                dividendData: [],
                allocationData: [],
                transactions: [],
                loading: false,
                error: null,
            });
        }
    }, [portfolioId]);

    return {
        ...state,
        addTransaction,
        refetch,
    };
};
