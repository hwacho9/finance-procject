"use client";

import { useState, useEffect, createContext, useContext } from "react";
import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut,
    onAuthStateChanged,
    GoogleAuthProvider,
    signInWithPopup,
    updateProfile,
    sendPasswordResetEmail,
    User as FirebaseUser,
} from "firebase/auth";
import { auth } from "@/lib/firebase";
import { userApi } from "@/lib/api";
import { Portfolio } from "@/types/portfolio";

export interface AuthUser {
    uid: string;
    email: string | null;
    displayName: string | null;
    photoURL: string | null;
    portfolios?: Portfolio[];
}

export interface AuthContextType {
    user: AuthUser | null;
    loading: boolean;
    error: string | null;
    signUp: (
        email: string,
        password: string,
        displayName?: string
    ) => Promise<void>;
    signIn: (email: string, password: string) => Promise<void>;
    signInWithGoogle: () => Promise<void>;
    logout: () => Promise<void>;
    resetPassword: (email: string) => Promise<void>;
    getIdToken: () => Promise<string | null>;
    clearError: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};

export const useAuthProvider = (): AuthContextType => {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const onAuthStateChangedHandler = async (
        firebaseUser: FirebaseUser | null
    ) => {
        if (firebaseUser) {
            try {
                // Get user data from backend, which now includes portfolios
                const backendUser = await userApi.getCurrentUser();
                setUser({
                    uid: firebaseUser.uid,
                    email: firebaseUser.email,
                    displayName: firebaseUser.displayName,
                    photoURL: firebaseUser.photoURL,
                    portfolios: backendUser.portfolios, // Set portfolios from backend
                });
            } catch (error) {
                console.error("Failed to fetch backend user data:", error);
                // Fallback to firebaseUser data if backend fails
                setUser({
                    uid: firebaseUser.uid,
                    email: firebaseUser.email,
                    displayName: firebaseUser.displayName,
                    photoURL: firebaseUser.photoURL,
                });
            }
        } else {
            setUser(null);
        }
        setLoading(false);
    };

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, onAuthStateChangedHandler);

        return unsubscribe;
    }, []);

    const signUp = async (
        email: string,
        password: string,
        displayName?: string
    ) => {
        try {
            setError(null);
            const { user: firebaseUser } = await createUserWithEmailAndPassword(
                auth,
                email,
                password
            );

            if (displayName && firebaseUser) {
                await updateProfile(firebaseUser, {
                    displayName,
                });
            }

            // Firebase 회원가입 성공 후 백엔드에 사용자 정보 저장
            if (firebaseUser) {
                try {
                    await userApi.getCurrentUser(); // 백엔드에서 사용자 생성 또는 조회
                    console.log("사용자 정보가 백엔드에 저장되었습니다.");
                } catch (backendError) {
                    console.error(
                        "백엔드 사용자 정보 저장 실패:",
                        backendError
                    );
                    // 백엔드 저장 실패는 치명적이지 않으므로 에러를 throw하지 않음
                }
            }
        } catch (error: unknown) {
            const message =
                error instanceof Error
                    ? error.message
                    : "An unknown error occurred";
            setError(message);
            throw new Error(message);
        }
    };

    const signIn = async (email: string, password: string) => {
        try {
            setError(null);
            await signInWithEmailAndPassword(auth, email, password);
        } catch (error: unknown) {
            const message =
                error instanceof Error
                    ? error.message
                    : "An unknown error occurred";
            setError(message);
            throw new Error(message);
        }
    };

    const signInWithGoogle = async () => {
        try {
            setError(null);
            const provider = new GoogleAuthProvider();
            provider.addScope("email");
            provider.addScope("profile");
            await signInWithPopup(auth, provider);
        } catch (error: unknown) {
            const message =
                error instanceof Error
                    ? error.message
                    : "An unknown error occurred";
            setError(message);
            throw new Error(message);
        }
    };

    const logout = async () => {
        try {
            await signOut(auth);
        } catch (error: unknown) {
            const message =
                error instanceof Error
                    ? error.message
                    : "An unknown error occurred";
            throw new Error(message);
        }
    };

    const resetPassword = async (email: string) => {
        try {
            await sendPasswordResetEmail(auth, email);
        } catch (error: unknown) {
            const message =
                error instanceof Error
                    ? error.message
                    : "An unknown error occurred";
            throw new Error(message);
        }
    };

    const getIdToken = async (): Promise<string | null> => {
        try {
            if (auth.currentUser) {
                return await auth.currentUser.getIdToken();
            }
            return null;
        } catch (error) {
            console.error("Error getting ID token:", error);
            return null;
        }
    };

    const clearError = () => {
        setError(null);
    };

    return {
        user,
        loading,
        error,
        signUp,
        signIn,
        signInWithGoogle,
        logout,
        resetPassword,
        getIdToken,
        clearError,
    };
};

export { AuthContext };
