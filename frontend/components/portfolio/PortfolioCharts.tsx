"use client";

import React from "react";
import {
    LineChart,
    Line,
    AreaChart,
    Area,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
import { format } from "date-fns";
import {
    PerformanceDataPoint,
    DividendDataPoint,
    AssetAllocation,
    PortfolioMetrics,
} from "@/types/portfolio";

// Color palette for charts
const COLORS = [
    "#0088FE",
    "#00C49F",
    "#FFBB28",
    "#FF8042",
    "#8884D8",
    "#82CA9D",
    "#FFC658",
    "#FF7C7C",
    "#8DD1E1",
    "#D084D0",
];

interface PortfolioValueChartProps {
    data: PerformanceDataPoint[];
    showInvested?: boolean;
}

export const PortfolioValueChart: React.FC<PortfolioValueChartProps> = ({
    data,
    showInvested = true,
}) => {
    const chartData = data.map((point) => {
        // Handle various date formats safely
        let formattedDate = "N/A";
        try {
            const date =
                typeof point.date === "string"
                    ? new Date(point.date)
                    : point.date;
            if (date && !isNaN(date.getTime())) {
                formattedDate = format(date, "MMM dd");
            } else {
                // Fallback: use the original string if it can't be parsed
                formattedDate = String(point.date).substring(0, 10);
            }
        } catch (error) {
            console.warn("Error parsing date:", point.date, error);
            formattedDate = String(point.date).substring(0, 10);
        }

        return {
            date: formattedDate,
            portfolio_value: point.portfolio_value,
            total_invested: point.total_invested,
            total_return: point.total_return,
        };
    });

    return (
        <div className="w-full h-80">
            {/* <h3 className="text-lg font-semibold mb-4">포트폴리오 가치 추이</h3> */}
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis
                        tickFormatter={(value) =>
                            `$${(value / 1000).toFixed(0)}K`
                        }
                    />
                    <Tooltip
                        formatter={(value: number) => [
                            `$${value.toLocaleString()}`,
                            "",
                        ]}
                        labelStyle={{ color: "#000" }}
                    />
                    <Legend />
                    <Line
                        type="monotone"
                        dataKey="portfolio_value"
                        stroke="#0088FE"
                        strokeWidth={2}
                        name="포트폴리오 가치"
                    />
                    {showInvested && (
                        <Line
                            type="monotone"
                            dataKey="total_invested"
                            stroke="#00C49F"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            name="총 투자금"
                        />
                    )}
                    <Line
                        type="monotone"
                        dataKey="total_return"
                        stroke="#FF8042"
                        strokeWidth={2}
                        name="총 수익"
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

interface DividendChartProps {
    data: DividendDataPoint[];
    chartType?: "monthly" | "cumulative";
}

export const DividendChart: React.FC<DividendChartProps> = ({
    data,
    chartType = "monthly",
}) => {
    const chartData = data.map((point) => {
        // Handle various date formats safely
        let formattedDate = "N/A";
        try {
            const date =
                typeof point.date === "string"
                    ? new Date(point.date)
                    : point.date;
            if (date && !isNaN(date.getTime())) {
                formattedDate = format(date, "MMM yy");
            } else {
                // Fallback: use the original string if it can't be parsed
                formattedDate = String(point.date).substring(0, 7); // YYYY-MM format
            }
        } catch (error) {
            console.warn("Error parsing date:", point.date, error);
            formattedDate = String(point.date).substring(0, 7);
        }

        return {
            date: formattedDate,
            monthly_dividend: point.monthly_dividend,
            cumulative_dividend: point.cumulative_dividend,
            dividend_yield: point.dividend_yield,
        };
    });

    if (chartType === "cumulative") {
        return (
            <div className="w-full h-80">
                <h3 className="text-lg font-semibold mb-4">누적 배당금</h3>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis
                            tickFormatter={(value) =>
                                `$${value.toLocaleString()}`
                            }
                        />
                        <Tooltip
                            formatter={(value: number) => [
                                `$${value.toLocaleString()}`,
                                "",
                            ]}
                        />
                        <Area
                            type="monotone"
                            dataKey="cumulative_dividend"
                            stroke="#00C49F"
                            fill="#00C49F"
                            fillOpacity={0.6}
                            name="누적 배당금"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        );
    }

    return (
        <div className="w-full h-80">
            <h3 className="text-lg font-semibold mb-4">월별 배당금</h3>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis
                        tickFormatter={(value) => `$${value.toLocaleString()}`}
                    />
                    <Tooltip
                        formatter={(value: number) => [
                            `$${value.toLocaleString()}`,
                            "",
                        ]}
                    />
                    <Bar
                        dataKey="monthly_dividend"
                        fill="#FFBB28"
                        name="월별 배당금"
                    />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

interface AssetAllocationChartProps {
    data: AssetAllocation[];
    chartType?: "pie" | "bar";
}

export const AssetAllocationChart: React.FC<AssetAllocationChartProps> = ({
    data,
    chartType = "pie",
}) => {
    const chartData = data.map((allocation) => ({
        name: allocation.symbol,
        value: allocation.percentage,
        amount: allocation.value,
    }));

    if (chartType === "bar") {
        return (
            <div className="w-full h-80">
                <h3 className="text-lg font-semibold mb-4">자산 배분 (비중)</h3>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} layout="horizontal">
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                            type="number"
                            tickFormatter={(value) => `${value.toFixed(1)}%`}
                        />
                        <YAxis type="category" dataKey="name" width={80} />
                        <Tooltip
                            formatter={(value: number) => [
                                `${value.toFixed(2)}%`,
                                "비중",
                            ]}
                        />
                        <Bar dataKey="value" fill="#0088FE" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        );
    }

    return (
        <div className="w-full h-80">
            {/* <h3 className="text-lg font-semibold mb-4">자산 배분</h3> */}
            <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, value }) =>
                            `${name}: ${value.toFixed(1)}%`
                        }>
                        {chartData.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                            />
                        ))}
                    </Pie>
                    <Tooltip
                        formatter={(value: number, name, props) => [
                            `${value.toFixed(2)}%`,
                            `$${props.payload.amount.toLocaleString()}`,
                        ]}
                    />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

interface SectorAllocationChartProps {
    data: Record<string, number>;
}

export const SectorAllocationChart: React.FC<SectorAllocationChartProps> = ({
    data,
}) => {
    const chartData = Object.entries(data).map(([sector, percentage]) => ({
        name: sector,
        value: percentage,
    }));

    return (
        <div className="w-full h-80">
            <h3 className="text-lg font-semibold mb-4">섹터별 배분</h3>
            <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, value }) =>
                            `${name}: ${value.toFixed(1)}%`
                        }>
                        {chartData.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                            />
                        ))}
                    </Pie>
                    <Tooltip
                        formatter={(value: number) => [
                            `${value.toFixed(2)}%`,
                            "비중",
                        ]}
                    />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

interface PerformanceMetricsDisplayProps {
    metrics: PortfolioMetrics;
}

export const PerformanceMetricsDisplay: React.FC<
    PerformanceMetricsDisplayProps
> = ({ metrics }) => {
    const metricsData = [
        {
            label: "총 수익률",
            value: metrics.total_return,
            format: (val: number) => `${val?.toFixed(2) || 0}%`,
            color: (val: number) =>
                val >= 0 ? "text-green-600" : "text-red-600",
        },
        {
            label: "연환산 수익률",
            value: metrics.annualized_return,
            format: (val: number) => `${val?.toFixed(2) || 0}%`,
            color: (val: number) =>
                val >= 0 ? "text-green-600" : "text-red-600",
        },
        {
            label: "변동성",
            value: metrics.volatility,
            format: (val: number) => `${val?.toFixed(2) || 0}%`,
            color: () => "text-gray-600",
        },
        {
            label: "샤프 비율",
            value: metrics.sharpe_ratio,
            format: (val: number) => `${val?.toFixed(2) || 0}`,
            color: () => "text-gray-600",
        },
        {
            label: "최대 낙폭",
            value: metrics.max_drawdown,
            format: (val: number) => `${val?.toFixed(2) || 0}%`,
            color: () => "text-red-600",
        },
        {
            label: "배당 수익률",
            value: metrics.dividend_yield,
            format: (val: number) => `${val?.toFixed(2) || 0}%`,
            color: () => "text-blue-600",
        },
    ];

    return (
        <div className="w-full">
            <h3 className="text-lg font-semibold mb-4">성과 지표</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {metricsData.map((metric, index) => (
                    <div
                        key={index}
                        className="bg-white p-4 rounded-lg shadow-sm border">
                        <div className="text-sm text-gray-500 mb-1">
                            {metric.label}
                        </div>
                        <div
                            className={`text-lg font-semibold ${metric.color(
                                metric.value || 0
                            )}`}>
                            {metric.format(metric.value || 0)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
