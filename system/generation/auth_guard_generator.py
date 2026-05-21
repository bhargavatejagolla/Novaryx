"""
NOVARYX - Auth Guard Generator
Generates authentication guard components and hooks.
"""


class AuthGuardGenerator:
    """Generates auth-related components"""
    
    @staticmethod
    def generate_protected_route() -> str:
        """Generate ProtectedRoute component"""
        return """import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: string
}

export function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const { user, loading, isAuthenticated } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-2 border-[var(--border)] border-t-[var(--primary)] rounded-full animate-spin" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />
  }

  return <>{children}</>
}
"""
    
    @staticmethod
    def generate_use_auth_hook() -> str:
        """Generate useAuth hook"""
        return """import { useState, useEffect, createContext, useContext } from 'react'

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
  login: async () => {},
  logout: async () => {},
  register: async () => {},
})

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
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
          headers: { Authorization: `Bearer ${token}` }
        })
        if (response.ok) {
          const userData = await response.json()
          setUser(userData)
        } else {
          localStorage.removeItem('auth_token')
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error)
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
        body: JSON.stringify({ email, password })
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
        body: JSON.stringify({ email, password, name })
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
"""
    
    @staticmethod
    def generate_login_page() -> str:
        """Generate login page"""
        return """import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login, loading } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      setError('Invalid email or password')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md p-8 rounded-2xl bg-gray-900 border border-white/5"
      >
        <h1 className="text-2xl font-bold text-white mb-6 text-center">
          Sign In
        </h1>
        
        {error && (
          <div className="p-3 mb-4 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2.5 rounded-xl bg-gray-800 border border-white/5 text-white focus:border-indigo-500/50 outline-none transition-colors"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2.5 rounded-xl bg-gray-800 border border-white/5 text-white focus:border-indigo-500/50 outline-none transition-colors"
              placeholder="Enter your password"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-500 transition-colors disabled:opacity-50 mt-2"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="text-gray-500 text-xs text-center mt-6">
          Don't have an account? <Link to="/register" className="text-indigo-400 hover:text-indigo-300">Sign up</Link>
        </p>
      </motion.div>
    </div>
  )
}
"""

    @staticmethod
    def generate_register_page() -> str:
        """Generate register page"""
        return """import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { register, loading } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await register(email, password, name)
      navigate('/')
    } catch (err) {
      setError('Registration failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md p-8 rounded-2xl bg-gray-900 border border-white/5"
      >
        <h1 className="text-2xl font-bold text-white mb-6 text-center">
          Create Account
        </h1>
        
        {error && (
          <div className="p-3 mb-4 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-4 py-2.5 rounded-xl bg-gray-800 border border-white/5 text-white focus:border-indigo-500/50 outline-none transition-colors"
              placeholder="Your Name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2.5 rounded-xl bg-gray-800 border border-white/5 text-white focus:border-indigo-500/50 outline-none transition-colors"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full px-4 py-2.5 rounded-xl bg-gray-800 border border-white/5 text-white focus:border-indigo-500/50 outline-none transition-colors"
              placeholder="Minimum 8 characters"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-500 transition-colors disabled:opacity-50 mt-2"
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>
        <p className="text-gray-500 text-xs text-center mt-6">
          Already have an account? <Link to="/login" className="text-indigo-400 hover:text-indigo-300">Sign in</Link>
        </p>
      </motion.div>
    </div>
  )
}
"""