"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { usePortfolio } from "@/hooks/usePortfolio";
import { Button } from "@/components/ui/Button";
import { PortfolioOverview } from "@/components/portfolio/PortfolioOverview";
import { HoldingsTable } from "@/components/portfolio/HoldingsTable";
import { TransactionForm } from "@/components/portfolio/TransactionForm";
import {
    DividendChart,
    SectorAllocationChart,
    PerformanceMetricsDisplay,
} from "@/components/portfolio/PortfolioCharts";
import { TransactionCreate, TransactionType } from "@/types/portfolio";

export default function PortfolioManagementPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();
    const [activeTab, setActiveTab] = useState("overview");
    const [showTransactionForm, setShowTransactionForm] = useState(false);

    // Get the first portfolio ID from the user object
    const portfolioId =
        user && user.portfolios && user.portfolios.length > 0
            ? user.portfolios[0].id
            : null;

    const {
        summary,
        performanceData,
        dividendData,
        allocationData,
        transactions,
        loading: portfolioLoading,
        error,
        addTransaction,
        refetch,
    } = usePortfolio(portfolioId);

    const handleTransactionSubmit = async (transaction: TransactionCreate) => {
        if (!portfolioId) {
            console.error("Cannot add transaction without a portfolio ID.");
            // Optionally show an error to the user via a toast notification
            return;
        }
        try {
            await addTransaction(transaction);
            setShowTransactionForm(false); // Close form on success
        } catch (error) {
            console.error("Failed to add transaction:", error);
            // You could show a toast notification here
        }
    };

    // Authentication check
    React.useEffect(() => {
        if (!authLoading && !user) {
            router.push("/login");
        }
    }, [user, authLoading, router]);

    if (authLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <h2 className="text-xl font-semibold text-gray-700">
                        인증 확인 중...
                    </h2>
                    <p className="text-gray-500 mt-2">잠시만 기다려 주세요</p>
                </div>
            </div>
        );
    }

    if (!user) {
        return null;
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg
                            className="w-8 h-8 text-red-600"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                    </div>
                    <h2 className="text-xl font-semibold text-gray-700 mb-2">
                        데이터 로딩 실패
                    </h2>
                    <p className="text-gray-500 mb-4">{error}</p>
                    <Button
                        onClick={refetch}
                        className="bg-blue-600 hover:bg-blue-700 text-white">
                        다시 시도
                    </Button>
                </div>
            </div>
        );
    }

    const tabs = [
        { id: "overview", name: "개요", icon: "📊" },
        { id: "holdings", name: "보유 종목", icon: "📈" },
        { id: "performance", name: "성과 분석", icon: "📋" },
        { id: "dividends", name: "배당 분석", icon: "💰" },
        { id: "transactions", name: "거래 내역", icon: "📝" },
    ];

    const getSectorAllocationData = () => {
        if (!allocationData || allocationData.length === 0) return {};

        const sectorData: { [key: string]: number } = {};
        allocationData.forEach((allocation) => {
            if (sectorData[allocation.sector]) {
                sectorData[allocation.sector] += allocation.percentage;
            } else {
                sectorData[allocation.sector] = allocation.percentage;
            }
        });
        return sectorData;
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            {/* 탭 네비게이션 */}
            <div className="bg-white border-b border-gray-200 sticky top-16 z-40">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between">
                        <div className="flex space-x-8 overflow-x-auto">
                            {tabs.map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`${
                                        activeTab === tab.id
                                            ? "border-blue-500 text-blue-600 bg-blue-50"
                                            : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                                    } whitespace-nowrap py-4 px-4 border-b-2 font-medium text-sm flex items-center space-x-2 rounded-t-lg transition-all duration-200`}>
                                    <span>{tab.icon}</span>
                                    <span>{tab.name}</span>
                                </button>
                            ))}
                        </div>
                        <div className="hidden md:block">
                            <Button
                                onClick={() => setShowTransactionForm(true)}
                                disabled={!portfolioId || portfolioLoading}
                                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium px-4 py-2 rounded-lg shadow-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed">
                                + 거래 추가
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            {/* 메인 컨텐츠 */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {activeTab === "overview" && (
                    <PortfolioOverview
                        summary={summary}
                        performanceData={performanceData}
                        allocationData={allocationData}
                        loading={portfolioLoading}
                    />
                )}

                {activeTab === "holdings" && (
                    <HoldingsTable
                        holdings={summary?.top_holdings || []}
                        loading={portfolioLoading}
                    />
                )}

                {activeTab === "performance" && (
                    <div className="space-y-8">
                        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">
                                성과 지표
                            </h3>
                            {portfolioLoading ? (
                                <div className="animate-pulse">
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        {[...Array(4)].map((_, i) => (
                                            <div
                                                key={i}
                                                className="h-20 bg-gray-200 rounded"></div>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <PerformanceMetricsDisplay
                                    metrics={{
                                        id: 1,
                                        portfolio_id: portfolioId!,
                                        metric_date: new Date().toISOString(),
                                        total_return:
                                            summary?.return_percentage || 0,
                                        annualized_return: 15.5,
                                        volatility: 18.2,
                                        sharpe_ratio: 1.25,
                                        max_drawdown: -8.5,
                                        dividend_yield: 2.8,
                                        created_at: new Date().toISOString(),
                                    }}
                                />
                            )}
                        </div>
                        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">
                                섹터별 배분
                            </h3>
                            {portfolioLoading ? (
                                <div className="animate-pulse">
                                    <div className="h-64 bg-gray-200 rounded"></div>
                                </div>
                            ) : (
                                <SectorAllocationChart
                                    data={getSectorAllocationData()}
                                />
                            )}
                        </div>
                    </div>
                )}

                {activeTab === "dividends" && (
                    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">
                            배당 분석
                        </h3>
                        {portfolioLoading ? (
                            <div className="animate-pulse">
                                <div className="h-64 bg-gray-200 rounded"></div>
                            </div>
                        ) : (
                            <DividendChart data={dividendData} />
                        )}
                    </div>
                )}

                {activeTab === "transactions" && (
                    <div className="bg-white rounded-xl shadow-lg border border-gray-100">
                        <div className="p-6 border-b border-gray-200">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900">
                                        거래 내역
                                    </h3>
                                    <p className="text-sm text-gray-600 mt-1">
                                        모든 매매 거래를 확인하세요
                                    </p>
                                </div>
                                <Button
                                    onClick={() => setShowTransactionForm(true)}
                                    disabled={!portfolioId || portfolioLoading}
                                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium px-4 py-2 rounded-lg shadow-md transition-all duration-200 md:hidden disabled:opacity-50 disabled:cursor-not-allowed">
                                    + 거래 추가
                                </Button>
                            </div>
                        </div>
                        <div className="p-6">
                            {portfolioLoading ? (
                                <div className="animate-pulse space-y-4">
                                    {[...Array(3)].map((_, i) => (
                                        <div
                                            key={i}
                                            className="h-16 bg-gray-200 rounded"></div>
                                    ))}
                                </div>
                            ) : transactions.length === 0 ? (
                                <div className="text-center py-8">
                                    <svg
                                        className="w-16 h-16 text-gray-400 mx-auto mb-4"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24">
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                        />
                                    </svg>
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                                        거래 내역이 없습니다
                                    </h3>
                                    <p className="text-gray-500 mb-4">
                                        첫 번째 거래를 추가해보세요!
                                    </p>
                                    <Button
                                        onClick={() =>
                                            setShowTransactionForm(true)
                                        }
                                        disabled={
                                            !portfolioId || portfolioLoading
                                        }
                                        className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed">
                                        거래 추가하기
                                    </Button>
                                </div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    종목
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    유형
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    수량
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    가격
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    날짜
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {transactions.map((transaction) => (
                                                <tr
                                                    key={transaction.id}
                                                    className="hover:bg-gray-50">
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                        {transaction.symbol}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span
                                                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                                                transaction.transaction_type ===
                                                                TransactionType.buy
                                                                    ? "bg-green-100 text-green-800"
                                                                    : transaction.transaction_type ===
                                                                      TransactionType.sell
                                                                    ? "bg-red-100 text-red-800"
                                                                    : "bg-blue-100 text-blue-800"
                                                            }`}>
                                                            {transaction.transaction_type ===
                                                            TransactionType.buy
                                                                ? "매수"
                                                                : transaction.transaction_type ===
                                                                  TransactionType.sell
                                                                ? "매도"
                                                                : "배당"}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                        {transaction.quantity}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                        ${transaction.price}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {new Date(
                                                            transaction.transaction_date
                                                        ).toLocaleDateString(
                                                            "ko-KR"
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* 거래 추가 모달 */}
            <TransactionForm
                isOpen={showTransactionForm}
                onClose={() => setShowTransactionForm(false)}
                onSubmit={handleTransactionSubmit}
                portfolioId={portfolioId}
            />
        </div>
    );
}
