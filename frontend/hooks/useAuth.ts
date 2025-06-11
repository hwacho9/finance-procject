import { useEffect } from "react";
import { useAuthStore } from "@/stores/auth";

export const useAuth = () => {
    const {
        user,
        loading,
        error,
        signUp,
        signIn,
        signOut,
        resetPassword,
        initializeAuth,
        setError,
    } = useAuthStore();

    useEffect(() => {
        const unsubscribe = initializeAuth();
        return unsubscribe;
    }, [initializeAuth]);

    const clearError = () => setError(null);

    return {
        user,
        loading,
        error,
        signUp,
        signIn,
        signOut,
        resetPassword,
        clearError,
    };
};
