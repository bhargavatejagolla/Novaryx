import React, { createContext, useContext, useState, ReactNode } from 'react'

interface ThemeContextType {
    theme: 'dark' | 'light'
    toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType>({
    theme: 'dark',
    toggleTheme: () => { },
})

export function useTheme() {
    return useContext(ThemeContext)
}

export function ThemeProvider({ children }: { children: ReactNode }) {
    const [theme, setTheme] = useState<'dark' | 'light'>('dark')

    const toggleTheme = () => {
        setTheme(prev => (prev === 'dark' ? 'light' : 'dark'))
    }

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            <div className={theme === 'dark' ? 'dark' : ''}>
                {children}
            </div>
        </ThemeContext.Provider>
    )
}

export default ThemeProvider
