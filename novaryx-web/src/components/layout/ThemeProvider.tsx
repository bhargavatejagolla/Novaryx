'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

export interface ThemeConfig {
    primary: string;
    accent: string;
    mode: 'dark' | 'light';
    font: string;
    borderRadius: string;
    glassmorphism: boolean;
}

interface ThemeContextType {
    theme: ThemeConfig;
    setTheme: (updates: Partial<ThemeConfig>) => void;
    toggleMode: () => void;
    resetTheme: () => void;
}

const defaultTheme: ThemeConfig = {
    primary: '#6366f1',
    accent: '#06b6d4',
    mode: 'dark',
    font: 'Inter',
    borderRadius: '12px',
    glassmorphism: true,
};

const ThemeContext = createContext<ThemeContextType>({
    theme: defaultTheme,
    setTheme: () => { },
    toggleMode: () => { },
    resetTheme: () => { },
});

export function useAppTheme() {
    return useContext(ThemeContext);
}

export function ThemeProvider({ children }: { children: ReactNode }) {
    const [theme, setThemeState] = useState<ThemeConfig>(defaultTheme);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        const stored = localStorage.getItem('novaryx-theme');
        if (stored) {
            try {
                const parsed = JSON.parse(stored);
                if (parsed && typeof parsed === 'object') {
                    setThemeState((prev) => ({ ...prev, ...parsed }));
                }
            } catch (e) {
                console.warn('Failed to parse stored theme, using defaults');
                localStorage.removeItem('novaryx-theme');
            }
        }
        setMounted(true);
    }, []);

    useEffect(() => {
        if (!mounted) return;

        const root = document.documentElement;
        root.classList.toggle('dark', theme.mode === 'dark');
        root.style.setProperty('--primary', theme.primary);
        root.style.setProperty('--accent', theme.accent);
        root.style.setProperty('--font', theme.font);
        root.style.setProperty('--radius', theme.borderRadius);

        localStorage.setItem('novaryx-theme', JSON.stringify(theme));
    }, [theme, mounted]);

    const setTheme = (updates: Partial<ThemeConfig>) => {
        setThemeState((prev) => ({ ...prev, ...updates }));
    };

    const toggleMode = () => {
        setThemeState((prev) => ({
            ...prev,
            mode: prev.mode === 'dark' ? 'light' : 'dark',
        }));
    };

    const resetTheme = () => setThemeState(defaultTheme);

    return (
        <ThemeContext.Provider value={{ theme, setTheme, toggleMode, resetTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}