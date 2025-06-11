import { User as FirebaseUser } from "firebase/auth";

export interface User {
    uid: string;
    email: string | null;
    displayName: string | null;
    photoURL: string | null;
    emailVerified: boolean;
}

export interface AuthContextType {
    user: User | null;
    loading: boolean;
    signUp: (
        email: string,
        password: string,
        displayName?: string
    ) => Promise<void>;
    signIn: (email: string, password: string) => Promise<void>;
    signOut: () => Promise<void>;
    resetPassword: (email: string) => Promise<void>;
}

export interface SignUpFormData {
    email: string;
    password: string;
    confirmPassword: string;
    displayName: string;
}

export interface SignInFormData {
    email: string;
    password: string;
}

export interface ResetPasswordFormData {
    email: string;
}

export type AuthError = {
    code: string;
    message: string;
};

// Convert Firebase User to our User type
export const mapFirebaseUser = (firebaseUser: FirebaseUser): User => ({
    uid: firebaseUser.uid,
    email: firebaseUser.email,
    displayName: firebaseUser.displayName,
    photoURL: firebaseUser.photoURL,
    emailVerified: firebaseUser.emailVerified,
});
