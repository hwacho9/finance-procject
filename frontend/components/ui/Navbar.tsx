"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth, AuthUser } from "@/hooks/useAuth";
import { Button } from "@/components/ui/Button";
import { useState, useCallback, Fragment } from "react";
import clsx from "clsx";

interface NavItem {
    name: string;
    href: string;
    icon?: React.ReactNode;
}

const NAV_ITEMS: NavItem[] = [
    {
        name: "대시보드",
        href: "/dashboard",
        icon: (
            <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor">
                <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"
                />
            </svg>
        ),
    },
    {
        name: "포트폴리오",
        href: "/portfolio-management",
        icon: (
            <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor">
                <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M21 12a2.25 2.25 0 00-2.25-2.25H15a3 3 0 11-6 0H5.25A2.25 2.25 0 003 12m18 0v6a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 18v-6m18 0V9M3 12V9m18 3a2.25 2.25 0 00-2.25-2.25H15a3 3 0 11-6 0H5.25A2.25 2.25 0 003 9m18 3h-5.25m-6.75 0H3"
                />
            </svg>
        ),
    },
];

const NavLink = ({
    item,
    isActive,
    onClick,
}: {
    item: NavItem;
    isActive: boolean;
    onClick?: () => void;
}) => (
    <Link
        href={item.href}
        onClick={onClick}
        className={clsx(
            "flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ease-in-out transform",
            isActive
                ? "bg-blue-50 text-blue-600"
                : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
        )}>
        <span className="w-5 h-5">{item.icon}</span>
        <span>{item.name}</span>
    </Link>
);

const UserMenu = ({
    user,
    onLogout,
}: {
    user: AuthUser | null;
    onLogout: () => void;
}) => {
    if (!user) return null;

    return (
        <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">
                        {(user.displayName ||
                            user.email ||
                            "U")[0].toUpperCase()}
                    </span>
                </div>
                <div className="hidden sm:block">
                    <p className="text-sm font-medium text-gray-900 truncate max-w-[120px]">
                        {user.displayName || user.email}
                    </p>
                </div>
            </div>
            <Button
                variant="outline"
                size="sm"
                onClick={onLogout}
                className="border-gray-300 hover:border-red-400 hover:text-red-600">
                로그아웃
            </Button>
        </div>
    );
};

export const Navbar = () => {
    const { user, loading, logout } = useAuth();
    const pathname = usePathname();
    const [mobileOpen, setMobileOpen] = useState(false);

    const toggleMobileMenu = useCallback(
        () => setMobileOpen((open) => !open),
        []
    );

    const handleLogout = useCallback(async () => {
        try {
            await logout();
            setMobileOpen(false);
        } catch (err) {
            console.error("로그아웃 실패:", err);
        }
    }, [logout]);

    return (
        <header
            role="banner"
            className="sticky top-0 z-50 bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center space-x-4">
                        <Link
                            href="/"
                            className="flex-shrink-0 flex items-center space-x-2 group">
                            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center transform group-hover:scale-110 transition-transform">
                                <svg
                                    className="w-5 h-5 text-white"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24">
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                                    />
                                </svg>
                            </div>
                            <span className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                                Macro Finance
                            </span>
                        </Link>
                        {user && (
                            <div className="hidden md:flex items-center space-x-2">
                                {NAV_ITEMS.map((item) => (
                                    <NavLink
                                        key={item.name}
                                        item={item}
                                        isActive={pathname.startsWith(
                                            item.href
                                        )}
                                    />
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="flex items-center space-x-3">
                        {loading ? (
                            <div className="animate-pulse flex items-center space-x-2">
                                <div className="h-8 w-8 bg-gray-200 rounded-full"></div>
                                <div className="h-4 w-20 bg-gray-200 rounded"></div>
                            </div>
                        ) : user ? (
                            <Fragment>
                                <div className="hidden md:flex">
                                    <UserMenu
                                        user={user}
                                        onLogout={handleLogout}
                                    />
                                </div>
                                <button
                                    onClick={toggleMobileMenu}
                                    aria-expanded={mobileOpen}
                                    aria-label="Toggle mobile menu"
                                    className="md:hidden p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100">
                                    {mobileOpen ? (
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
                                    ) : (
                                        <svg
                                            className="w-6 h-6"
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24">
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M4 6h16M4 12h16M4 18h16"
                                            />
                                        </svg>
                                    )}
                                </button>
                            </Fragment>
                        ) : (
                            <div className="flex items-center space-x-2">
                                <Link href="/login">
                                    <Button variant="outline" size="sm">
                                        로그인
                                    </Button>
                                </Link>
                                <Link href="/register">
                                    <Button size="sm">회원가입</Button>
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileOpen && user && (
                <div className="md:hidden bg-white border-t border-gray-200">
                    <div className="px-2 py-2 flex space-x-2">
                        {NAV_ITEMS.map((item) => (
                            <NavLink
                                key={item.name}
                                item={item}
                                isActive={pathname.startsWith(item.href)}
                                onClick={toggleMobileMenu}
                            />
                        ))}
                    </div>
                    <div className="px-4 py-4 border-t border-gray-200">
                        <UserMenu user={user} onLogout={handleLogout} />
                    </div>
                </div>
            )}
        </header>
    );
};
