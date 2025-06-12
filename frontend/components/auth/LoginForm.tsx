"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/hooks/useAuth";
import { Loader2 } from "lucide-react";

interface LoginFormProps {
    onSuccess?: () => void;
}

export default function LoginForm({ onSuccess }: LoginFormProps) {
    const { signIn, signUp, signInWithGoogle } = useAuth();
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [formData, setFormData] = useState({
        email: "",
        password: "",
        displayName: "",
        confirmPassword: "",
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            if (isLogin) {
                await signIn(formData.email, formData.password);
            } else {
                if (formData.password !== formData.confirmPassword) {
                    throw new Error("비밀번호가 일치하지 않습니다.");
                }
                await signUp(
                    formData.email,
                    formData.password,
                    formData.displayName
                );
            }
            onSuccess?.();
        } catch (error: unknown) {
            const message =
                error instanceof Error ? error.message : "An error occurred";
            setError(message);
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleSignIn = async () => {
        setError("");
        setLoading(true);

        try {
            await signInWithGoogle();
            onSuccess?.();
        } catch (error: unknown) {
            const message =
                error instanceof Error ? error.message : "An error occurred";
            setError(message);
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (field: string, value: string) => {
        setFormData((prev) => ({ ...prev, [field]: value }));
    };

    return (
        <div className="w-full max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
            <div className="text-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">
                    {isLogin ? "로그인" : "회원가입"}
                </h1>
                <p className="text-gray-600 mt-2">
                    {isLogin
                        ? "포트폴리오 관리 시스템에 로그인하세요"
                        : "새 계정을 만들어 시작하세요"}
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                {!isLogin && (
                    <div>
                        <label
                            htmlFor="displayName"
                            className="block text-sm font-medium text-gray-700 mb-1">
                            이름
                        </label>
                        <Input
                            id="displayName"
                            type="text"
                            placeholder="홍길동"
                            value={formData.displayName}
                            onChange={(e) =>
                                handleInputChange("displayName", e.target.value)
                            }
                            required={!isLogin}
                        />
                    </div>
                )}

                <div>
                    <label
                        htmlFor="email"
                        className="block text-sm font-medium text-gray-700 mb-1">
                        이메일
                    </label>
                    <Input
                        id="email"
                        type="email"
                        placeholder="email@example.com"
                        value={formData.email}
                        onChange={(e) =>
                            handleInputChange("email", e.target.value)
                        }
                        required
                    />
                </div>

                <div>
                    <label
                        htmlFor="password"
                        className="block text-sm font-medium text-gray-700 mb-1">
                        비밀번호
                    </label>
                    <Input
                        id="password"
                        type="password"
                        placeholder="••••••••"
                        value={formData.password}
                        onChange={(e) =>
                            handleInputChange("password", e.target.value)
                        }
                        required
                    />
                </div>

                {!isLogin && (
                    <div>
                        <label
                            htmlFor="confirmPassword"
                            className="block text-sm font-medium text-gray-700 mb-1">
                            비밀번호 확인
                        </label>
                        <Input
                            id="confirmPassword"
                            type="password"
                            placeholder="••••••••"
                            value={formData.confirmPassword}
                            onChange={(e) =>
                                handleInputChange(
                                    "confirmPassword",
                                    e.target.value
                                )
                            }
                            required={!isLogin}
                        />
                    </div>
                )}

                {error && (
                    <div className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">
                        {error}
                    </div>
                )}

                <Button type="submit" className="w-full" disabled={loading}>
                    {loading && (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    {isLogin ? "로그인" : "계정 만들기"}
                </Button>
            </form>

            <div className="mt-4">
                <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-gray-300" />
                    </div>
                    <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-white text-gray-500">
                            또는
                        </span>
                    </div>
                </div>

                <Button
                    type="button"
                    variant="outline"
                    className="w-full mt-4"
                    onClick={handleGoogleSignIn}
                    disabled={loading}>
                    {loading && (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    Google로 계속하기
                </Button>
            </div>

            <div className="text-center text-sm mt-4">
                <button
                    type="button"
                    className="text-blue-600 hover:text-blue-500 hover:underline"
                    onClick={() => setIsLogin(!isLogin)}>
                    {isLogin
                        ? "계정이 없으신가요? 회원가입"
                        : "이미 계정이 있으신가요? 로그인"}
                </button>
            </div>
        </div>
    );
}
