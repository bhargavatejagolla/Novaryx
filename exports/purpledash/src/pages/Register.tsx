import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import { Mail, Lock, User, Eye, EyeOff, Zap } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

export default function Register() {
    const [name, setName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [showPw, setShowPw] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const { register } = useAuth()
    const navigate = useNavigate()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            await register(email, password, name)
            navigate('/')
        } catch {
            setError('Registration failed. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
            </div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} className="w-full max-w-sm relative z-10">
                <div className="flex items-center gap-2 justify-center mb-8">
                    <div className="w-9 h-9 bg-indigo-600 rounded-xl flex items-center justify-center">
                        <Zap size={18} className="text-white" />
                    </div>
                    <span className="text-white font-bold text-xl">PurpleDash</span>
                </div>

                <div className="bg-gray-900 border border-white/5 rounded-2xl p-8">
                    <h2 className="text-white font-bold text-2xl text-center">Create account</h2>
                    <p className="text-gray-500 text-sm text-center mt-1 mb-6">Get started for free today</p>

                    {error && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs">
                            {error}
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {[
                            { label: 'Full Name', icon: <User size={14} />, value: name, set: setName, type: 'text', placeholder: 'Alice Chen' },
                            { label: 'Email', icon: <Mail size={14} />, value: email, set: setEmail, type: 'email', placeholder: 'you@company.com' },
                        ].map(f => (
                            <div key={f.label}>
                                <label className="text-gray-500 text-xs mb-1.5 block">{f.label}</label>
                                <div className="relative">
                                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600">{f.icon}</span>
                                    <input type={f.type} value={f.value} onChange={e => f.set(e.target.value)} placeholder={f.placeholder} required
                                        className="w-full bg-gray-800 border border-white/5 rounded-xl pl-9 pr-4 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500/50 transition-colors" />
                                </div>
                            </div>
                        ))}
                        <div>
                            <label className="text-gray-500 text-xs mb-1.5 block">Password</label>
                            <div className="relative">
                                <Lock size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600" />
                                <input type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="Min 8 characters" required minLength={8}
                                    className="w-full bg-gray-800 border border-white/5 rounded-xl pl-9 pr-10 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500/50 transition-colors" />
                                <button type="button" onClick={() => setShowPw(s => !s)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-400 transition-colors">
                                    {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
                                </button>
                            </div>
                        </div>

                        <motion.button type="submit" disabled={loading} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white font-medium text-sm rounded-xl transition-colors flex items-center justify-center gap-2 mt-2">
                            {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Create Account'}
                        </motion.button>
                    </form>

                    <p className="text-gray-600 text-xs text-center mt-6">
                        Already have an account?{' '}
                        <Link to="/login" className="text-indigo-400 hover:text-indigo-300 transition-colors">Sign in</Link>
                    </p>
                </div>
            </motion.div>
        </div>
    )
}
