import React, { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
    LayoutDashboard, BarChart3, Users, Settings, Bell,
    HelpCircle, User, LogOut, ChevronLeft, TrendingUp, Menu
} from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

const navItems = [
    { label: 'Dashboard', icon: LayoutDashboard, to: '/dashboard' },
    { label: 'Analytics', icon: BarChart3, to: '/dashboard/analytics' },
    { label: 'Stats', icon: TrendingUp, to: '/dashboard/stats' },
    { label: 'Users', icon: Users, to: '/settings/users' },
    { label: 'Notifications', icon: Bell, to: '/settings/notifications' },
    { label: 'Settings', icon: Settings, to: '/settings' },
    { label: 'Profile', icon: User, to: '/settings/profile' },
    { label: 'Help', icon: HelpCircle, to: '/help' },
]

export default function DashboardLayout() {
    const [collapsed, setCollapsed] = useState(false)
    const { user, logout } = useAuth()
    const navigate = useNavigate()

    const handleLogout = async () => {
        await logout()
        navigate('/login')
    }

    return (
        <div className="min-h-screen bg-gray-950 flex">
            {/* Sidebar */}
            <motion.aside
                animate={{ width: collapsed ? 72 : 240 }}
                transition={{ duration: 0.25, ease: 'easeInOut' }}
                className="bg-gray-900 border-r border-white/5 flex flex-col h-screen sticky top-0 overflow-hidden"
            >
                {/* Logo */}
                <div className="h-16 flex items-center justify-between px-4 border-b border-white/5">
                    <AnimatePresence>
                        {!collapsed && (
                            <motion.span
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="text-white font-bold text-lg tracking-tight"
                            >
                                PurpleDash
                            </motion.span>
                        )}
                    </AnimatePresence>
                    <button
                        onClick={() => setCollapsed(c => !c)}
                        className="p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-colors ml-auto"
                    >
                        <motion.div animate={{ rotate: collapsed ? 180 : 0 }} transition={{ duration: 0.25 }}>
                            <ChevronLeft size={18} />
                        </motion.div>
                    </button>
                </div>

                {/* Nav */}
                <nav className="flex-1 py-4 px-2 space-y-0.5 overflow-y-auto">
                    {navItems.map(item => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group
                ${isActive
                                    ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/20'
                                    : 'text-gray-500 hover:text-white hover:bg-white/5'
                                }`
                            }
                        >
                            <item.icon size={18} className="shrink-0" />
                            <AnimatePresence>
                                {!collapsed && (
                                    <motion.span
                                        initial={{ opacity: 0, width: 0 }}
                                        animate={{ opacity: 1, width: 'auto' }}
                                        exit={{ opacity: 0, width: 0 }}
                                        className="overflow-hidden whitespace-nowrap"
                                    >
                                        {item.label}
                                    </motion.span>
                                )}
                            </AnimatePresence>
                        </NavLink>
                    ))}
                </nav>

                {/* User footer */}
                <div className="p-3 border-t border-white/5">
                    <div className={`flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 transition-colors ${collapsed ? 'justify-center' : ''}`}>
                        <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 text-sm font-bold shrink-0">
                            {user?.name?.[0]?.toUpperCase() ?? 'U'}
                        </div>
                        <AnimatePresence>
                            {!collapsed && (
                                <motion.div
                                    initial={{ opacity: 0, width: 0 }}
                                    animate={{ opacity: 1, width: 'auto' }}
                                    exit={{ opacity: 0, width: 0 }}
                                    className="flex-1 min-w-0 overflow-hidden"
                                >
                                    <p className="text-white text-xs font-medium truncate">{user?.name ?? 'User'}</p>
                                    <p className="text-gray-600 text-xs truncate">{user?.email ?? ''}</p>
                                </motion.div>
                            )}
                        </AnimatePresence>
                        {!collapsed && (
                            <button onClick={handleLogout} className="p-1 text-gray-600 hover:text-red-400 transition-colors">
                                <LogOut size={15} />
                            </button>
                        )}
                    </div>
                </div>
            </motion.aside>

            {/* Main content */}
            <main className="flex-1 overflow-auto">
                <Outlet />
            </main>
        </div>
    )
}
