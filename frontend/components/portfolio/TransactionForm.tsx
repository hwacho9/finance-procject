import React, { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { TransactionCreate, TransactionType } from "@/types/portfolio";

interface TransactionFormProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (transaction: TransactionCreate) => Promise<void>;
    portfolioId: number | null;
}

export const TransactionForm: React.FC<TransactionFormProps> = ({
    isOpen,
    onClose,
    onSubmit,
    portfolioId,
}) => {
    const [formData, setFormData] = useState<TransactionCreate>({
        symbol: "",
        transaction_type: TransactionType.BUY,
        quantity: 0,
        price: 0,
        transaction_date: new Date().toISOString().split("T")[0],
        fees: 0,
        notes: "",
    });

    const [submitLoading, setSubmitLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!portfolioId) {
            console.error("Portfolio ID is missing, cannot submit.");
            // You can show a user-facing error here
            return;
        }
        try {
            setSubmitLoading(true);
            await onSubmit(formData);

            // Reset form
            setFormData({
                symbol: "",
                transaction_type: TransactionType.BUY,
                quantity: 0,
                price: 0,
                transaction_date: new Date().toISOString().split("T")[0],
                fees: 0,
                notes: "",
            });

            onClose();
        } catch (error) {
            console.error("Failed to submit transaction:", error);
        } finally {
            setSubmitLoading(false);
        }
    };

    const handleInputChange = (
        field: keyof TransactionCreate,
        value: string | number | TransactionType
    ) => {
        setFormData((prev) => ({ ...prev, [field]: value }));
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
                <div className="p-6 border-b border-gray-200">
                    <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-gray-900">
                            새 거래 추가
                        </h3>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600 transition-colors"
                            disabled={submitLoading}>
                            <svg
                                className="w-6 h-6"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M6 18L18 6M6 6l12 12"
                                />
                            </svg>
                        </button>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            종목 심볼
                        </label>
                        <Input
                            type="text"
                            placeholder="예: AAPL"
                            value={formData.symbol}
                            onChange={(e) =>
                                handleInputChange(
                                    "symbol",
                                    e.target.value.toUpperCase()
                                )
                            }
                            className="w-full"
                            required
                            disabled={submitLoading}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            거래 유형
                        </label>
                        <select
                            value={formData.transaction_type}
                            onChange={(e) =>
                                handleInputChange(
                                    "transaction_type",
                                    e.target.value as TransactionType
                                )
                            }
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            disabled={submitLoading}>
                            <option value={TransactionType.BUY}>매수</option>
                            <option value={TransactionType.SELL}>매도</option>
                            <option value={TransactionType.DIVIDEND}>
                                배당
                            </option>
                        </select>
                    </div>

                    {formData.transaction_type !== TransactionType.DIVIDEND ? (
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    수량
                                </label>
                                <Input
                                    type="number"
                                    placeholder="10"
                                    value={formData.quantity || ""}
                                    onChange={(e) =>
                                        handleInputChange(
                                            "quantity",
                                            Number(e.target.value)
                                        )
                                    }
                                    required={
                                        formData.transaction_type ===
                                            TransactionType.BUY ||
                                        formData.transaction_type ===
                                            TransactionType.SELL
                                    }
                                    disabled={submitLoading}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    단가 ($)
                                </label>
                                <Input
                                    type="number"
                                    step="0.01"
                                    placeholder="150.00"
                                    value={formData.price || ""}
                                    onChange={(e) =>
                                        handleInputChange(
                                            "price",
                                            Number(e.target.value)
                                        )
                                    }
                                    required={
                                        formData.transaction_type ===
                                            TransactionType.BUY ||
                                        formData.transaction_type ===
                                            TransactionType.SELL
                                    }
                                    disabled={submitLoading}
                                />
                            </div>
                        </div>
                    ) : (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                총 배당금 ($)
                            </label>
                            <Input
                                type="number"
                                step="0.01"
                                placeholder="50.00"
                                value={formData.price || ""}
                                onChange={(e) => {
                                    handleInputChange(
                                        "price",
                                        Number(e.target.value)
                                    );
                                    handleInputChange("quantity", 1);
                                }}
                                required
                                disabled={submitLoading}
                            />
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            거래일
                        </label>
                        <Input
                            type="date"
                            value={formData.transaction_date}
                            onChange={(e) =>
                                handleInputChange(
                                    "transaction_date",
                                    e.target.value
                                )
                            }
                            required
                            disabled={submitLoading}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            수수료 ($)
                        </label>
                        <Input
                            type="number"
                            step="0.01"
                            placeholder="0.00"
                            value={formData.fees || ""}
                            onChange={(e) =>
                                handleInputChange(
                                    "fees",
                                    Number(e.target.value)
                                )
                            }
                            disabled={submitLoading}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            메모
                        </label>
                        <textarea
                            placeholder="거래에 대한 메모를 입력하세요"
                            value={formData.notes}
                            onChange={(e) =>
                                handleInputChange("notes", e.target.value)
                            }
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                            rows={3}
                            disabled={submitLoading}
                        />
                    </div>

                    <div className="flex space-x-3 pt-4">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={onClose}
                            className="flex-1"
                            disabled={submitLoading}>
                            취소
                        </Button>
                        <Button
                            type="submit"
                            className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                            disabled={submitLoading}>
                            {submitLoading ? "처리중..." : "거래 추가"}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
};
