import { useState, useEffect } from "react";
import { portfolioAPI } from "@/lib/api/portfolio";
import { Portfolio } from "@/types/portfolio";

interface UsePortfoliosState {
    portfolios: Portfolio[];
    loading: boolean;
    error: string | null;
}

export const usePortfolios = () => {
    const [state, setState] = useState<UsePortfoliosState>({
        portfolios: [],
        loading: true,
        error: null,
    });

    const fetchPortfolios = async () => {
        try {
            setState({ portfolios: [], loading: true, error: null });
            const portfolios = await portfolioAPI.getPortfolios();
            setState({ portfolios, loading: false, error: null });
        } catch (error) {
            console.error("Failed to fetch portfolios:", error);
            setState({
                portfolios: [],
                loading: false,
                error:
                    error instanceof Error
                        ? error.message
                        : "Failed to fetch portfolios",
            });
        }
    };

    useEffect(() => {
        fetchPortfolios();
    }, []);

    return {
        ...state,
        refetch: fetchPortfolios,
    };
};
