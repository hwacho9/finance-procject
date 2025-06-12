import React from "react";
import { Holding } from "@/types/portfolio";

interface HoldingsTableProps {
    holdings: Holding[];
    loading: boolean;
}

export const HoldingsTable: React.FC<HoldingsTableProps> = ({
    holdings,
    loading,
}) => {
    if (loading) {
        return (
            <div className="bg-white rounded-xl shadow-lg border border-gray-100">
                <div className="p-6 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900">
                        보유 종목
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                        현재 보유 중인 모든 종목을 확인하세요
                    </p>
                </div>
                <div className="p-6">
                    <div className="animate-pulse space-y-4">
                        {[...Array(3)].map((_, i) => (
                            <div
                                key={i}
                                className="flex items-center space-x-4">
                                <div className="w-10 h-10 bg-gray-200 rounded-lg"></div>
                                <div className="flex-1 space-y-2">
                                    <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                                    <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                                </div>
                                <div className="space-y-2">
                                    <div className="h-4 bg-gray-200 rounded w-16"></div>
                                    <div className="h-3 bg-gray-200 rounded w-12"></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100">
            <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                    보유 종목
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                    현재 보유 중인 모든 종목을 확인하세요
                </p>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                종목
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                섹터
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                수량
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                평균단가
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                현재가
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                평가금액
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                손익
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {holdings.map((holding) => (
                            <tr
                                key={holding.id}
                                className="hover:bg-gray-50 transition-colors duration-200">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center">
                                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-3">
                                            <span className="text-white font-semibold text-sm">
                                                {holding.symbol.slice(0, 2)}
                                            </span>
                                        </div>
                                        <div>
                                            <div className="text-sm font-medium text-gray-900">
                                                {holding.symbol}
                                            </div>
                                            <div className="text-sm text-gray-500">
                                                {holding.company_name}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                        {holding.sector}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {holding.quantity}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    ${holding.average_cost}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    ${holding.current_price}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    $
                                    {(
                                        holding.current_value || 0
                                    ).toLocaleString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <div
                                        className={`flex items-center ${
                                            (holding.unrealized_gain_loss ||
                                                0) >= 0
                                                ? "text-green-600"
                                                : "text-red-600"
                                        }`}>
                                        <span className="font-medium">
                                            {(holding.unrealized_gain_loss ||
                                                0) >= 0
                                                ? "+"
                                                : ""}
                                            $
                                            {(
                                                holding.unrealized_gain_loss ||
                                                0
                                            ).toLocaleString()}
                                        </span>
                                        <span className="ml-2 text-xs">
                                            (
                                            {(
                                                holding.unrealized_gain_loss_percent ||
                                                0
                                            ).toFixed(2)}
                                            %)
                                        </span>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
