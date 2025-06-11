import { create } from "zustand";
import {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut as firebaseSignOut,
    sendPasswordResetEmail,
    updateProfile,
    onAuthStateChanged,
    User as FirebaseUser,
} from "firebase/auth";
import { auth } from "@/lib/firebase";
import { User, mapFirebaseUser, AuthError } from "@/types/auth";

interface AuthState {
    user: User | null;
    loading: boolean;
    error: string | null;
}

interface AuthActions {
    setUser: (user: User | null) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
    signUp: (
        email: string,
        password: string,
        displayName?: string
    ) => Promise<void>;
    signIn: (email: string, password: string) => Promise<void>;
    signOut: () => Promise<void>;
    resetPassword: (email: string) => Promise<void>;
    initializeAuth: () => () => void;
}

export const useAuthStore = create<AuthState & AuthActions>((set, get) => ({
    user: null,
    loading: true,
    error: null,

    setUser: (user) => set({ user }),
    setLoading: (loading) => set({ loading }),
    setError: (error) => set({ error }),

    signUp: async (email, password, displayName) => {
        try {
            set({ loading: true, error: null });

            const userCredential = await createUserWithEmailAndPassword(
                auth,
                email,
                password
            );

            // Update display name if provided
            if (displayName && userCredential.user) {
                await updateProfile(userCredential.user, { displayName });
            }

            set({ loading: false });
        } catch (error: any) {
            const authError = error as AuthError;
            set({
                loading: false,
                error: getAuthErrorMessage(authError.code),
            });
            throw error;
        }
    },

    signIn: async (email, password) => {
        try {
            set({ loading: true, error: null });

            await signInWithEmailAndPassword(auth, email, password);

            set({ loading: false });
        } catch (error: any) {
            const authError = error as AuthError;
            set({
                loading: false,
                error: getAuthErrorMessage(authError.code),
            });
            throw error;
        }
    },

    signOut: async () => {
        try {
            set({ loading: true, error: null });

            await firebaseSignOut(auth);

            set({ user: null, loading: false });
        } catch (error: any) {
            const authError = error as AuthError;
            set({
                loading: false,
                error: getAuthErrorMessage(authError.code),
            });
            throw error;
        }
    },

    resetPassword: async (email) => {
        try {
            set({ loading: true, error: null });

            await sendPasswordResetEmail(auth, email);

            set({ loading: false });
        } catch (error: any) {
            const authError = error as AuthError;
            set({
                loading: false,
                error: getAuthErrorMessage(authError.code),
            });
            throw error;
        }
    },

    initializeAuth: () => {
        const unsubscribe = onAuthStateChanged(
            auth,
            (firebaseUser: FirebaseUser | null) => {
                if (firebaseUser) {
                    const user = mapFirebaseUser(firebaseUser);
                    set({ user, loading: false });
                } else {
                    set({ user: null, loading: false });
                }
            }
        );

        return unsubscribe;
    },
}));

// Helper function to convert Firebase auth error codes to user-friendly messages
const getAuthErrorMessage = (errorCode: string): string => {
    switch (errorCode) {
        case "auth/user-not-found":
            return "이메일 주소를 찾을 수 없습니다.";
        case "auth/wrong-password":
            return "비밀번호가 올바르지 않습니다.";
        case "auth/email-already-in-use":
            return "이미 사용 중인 이메일 주소입니다.";
        case "auth/weak-password":
            return "비밀번호는 최소 6자 이상이어야 합니다.";
        case "auth/invalid-email":
            return "유효하지 않은 이메일 주소입니다.";
        case "auth/too-many-requests":
            return "너무 많은 요청이 발생했습니다. 잠시 후 다시 시도해주세요.";
        case "auth/network-request-failed":
            return "네트워크 연결을 확인해주세요.";
        default:
            return "인증 중 오류가 발생했습니다. 다시 시도해주세요.";
    }
};
