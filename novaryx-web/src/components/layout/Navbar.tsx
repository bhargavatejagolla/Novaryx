'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Sparkles, LayoutDashboard, Wand2, Eye, FolderOpen,
    Settings, Download, Menu, X, Zap
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
    { href: '/', label: 'Home', icon: Sparkles },
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/builder', label: 'Builder', icon: Wand2 },
];

export function Navbar() {
    const pathname = usePathname();
    const [mobileOpen, setMobileOpen] = useState(false);

    return (
        <>
            <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-xl border-b border-white/10">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 group">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--primary)] to-accent flex items-center justify-center">
                            <Zap className="w-4 h-4 text-white" />
                        </div>
                        <span className="text-lg font-bold text-white">
                            NOVARYX
                        </span>
                    </Link>

                    {/* Desktop Nav */}
                    <div className="hidden md:flex items-center gap-1">
                        {navItems.map((item) => {
                            const isActive = pathname === item.href ||
                                (item.href !== '/' && pathname?.startsWith(item.href));
                            const Icon = item.icon;

                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        'relative px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-2',
                                        isActive
                                            ? 'text-white'
                                            : 'text-gray-500 hover:text-gray-300'
                                    )}
                                >
                                    {isActive && (
                                        <motion.div
                                            layoutId="navbar-active"
                                            className="absolute inset-0 bg-white/10 rounded-xl"
                                            transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                                        />
                                    )}
                                    <span className="relative z-10 flex items-center gap-2">
                                        <Icon className="w-4 h-4" />
                                        {item.label}
                                    </span>
                                </Link>
                            );
                        })}
                    </div>

                    {/* Right */}
                    <div className="hidden md:flex items-center gap-3">
                        <Link
                            href="/builder"
                            className="px-5 py-2 rounded-xl bg-[var(--primary)] text-white text-sm font-medium hover:shadow-[0_0_25px_rgba(99,102,241,0.4)] transition-shadow flex items-center gap-2"
                        >
                            <Wand2 className="w-4 h-4" />
                            Start Building
                        </Link>
                    </div>

                    {/* Mobile Toggle */}
                    <button
                        onClick={() => setMobileOpen(!mobileOpen)}
                        className="md:hidden p-2 rounded-lg text-white hover:bg-white/10 transition-colors"
                    >
                        {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                    </button>
                </div>
            </nav>

            {/* Mobile Menu */}
            <AnimatePresence>
                {mobileOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="fixed inset-x-0 top-16 z-40 md:hidden bg-background/95 backdrop-blur-xl border-b border-white/10"
                    >
                        <div className="px-4 py-4 space-y-1">
                            {navItems.map((item) => {
                                const isActive = pathname === item.href;
                                const Icon = item.icon;

                                return (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        onClick={() => setMobileOpen(false)}
                                        className={cn(
                                            'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all',
                                            isActive
                                                ? 'bg-[var(--primary)]/10 text-[var(--primary)]'
                                                : 'text-gray-400 hover:bg-white/5 hover:text-white'
                                        )}
                                    >
                                        <Icon className="w-4 h-4" />
                                        {item.label}
                                    </Link>
                                );
                            })}
                            <Link
                                href="/builder"
                                onClick={() => setMobileOpen(false)}
                                className="flex items-center gap-3 px-4 py-3 mt-2 rounded-xl bg-[var(--primary)] text-white text-sm font-medium"
                            >
                                <Wand2 className="w-4 h-4" />
                                Start Building
                            </Link>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}