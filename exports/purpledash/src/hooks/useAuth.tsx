import { useState, useEffect, createContext, useContext, ReactNode } from 'react'

interface User {
    id: string
    email: string
    name?: string
    role?: string
    avatar?: string
}

interface AuthContextType {
    user: User | null
    loading: boolean
    isAuthenticated: boolean
    login: (email: string, password: string) => Promise<void>
    logout: () => Promise<void>
    register: (email: string, password: string, name: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    loading: true,
    isAuthenticated: false,
    login: async () => { },
    logout: async () => { },
    register: async () => { },
})

export function useAuth() {
    return useContext(AuthContext)
}

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        checkAuth()
    }, [])

    async function checkAuth() {
        try {
            const token = localStorage.getItem('auth_token')
            if (token) {
                const response = await fetch('/api/auth/me', {
                    headers: { Authorization: `Bearer ${token}` },
                })
                if (response.ok) {
                    const userData = await response.json()
                    setUser(userData)
                } else {
                    localStorage.removeItem('auth_token')
                }
            }
        } catch {
            // silent fail
        } finally {
            setLoading(false)
        }
    }

    async function login(email: string, password: string) {
        setLoading(true)
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            })
            if (response.ok) {
                const data = await response.json()
                localStorage.setItem('auth_token', data.token)
                setUser(data.user)
            } else {
                throw new Error('Login failed')
            }
        } finally {
            setLoading(false)
        }
    }

    async function logout() {
        localStorage.removeItem('auth_token')
        setUser(null)
    }

    async function register(email: string, password: string, name: string) {
        setLoading(true)
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, name }),
            })
            if (response.ok) {
                const data = await response.json()
                localStorage.setItem('auth_token', data.token)
                setUser(data.user)
            } else {
                throw new Error('Registration failed')
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <AuthContext.Provider value={{ user, loading, isAuthenticated: !!user, login, logout, register }}>
            {children}
        </AuthContext.Provider>
    )
}
