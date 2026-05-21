import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Users, BarChart3, DollarSign, Activity } from 'lucide-react'

interface StatCardProps {
    title: string
    value: string
    change: string
    changeType: 'up' | 'down'
    icon: React.ReactNode
    color: string
}

function StatCard({ title, value, change, changeType, icon, color }: StatCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02, y: -2 }}
            transition={{ duration: 0.3 }}
            className="bg-gray-900 border border-white/5 rounded-2xl p-6 flex flex-col gap-4 hover:border-white/10 transition-all duration-300"
        >
            <div className="flex items-center justify-between">
                <span className="text-gray-400 text-sm font-medium">{title}</span>
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color}`}>
                    {icon}
                </div>
            </div>
            <div>
                <p className="text-3xl font-bold text-white">{value}</p>
                <div className="flex items-center gap-1 mt-1">
                    {changeType === 'up' ? (
                        <TrendingUp size={14} className="text-emerald-400" />
                    ) : (
                        <TrendingDown size={14} className="text-red-400" />
                    )}
                    <span className={`text-xs font-medium ${changeType === 'up' ? 'text-emerald-400' : 'text-red-400'}`}>
                        {change} vs last month
                    </span>
                </div>
            </div>
        </motion.div>
    )
}

export default function StatsCards() {
    const stats = [
        {
            title: 'Total Users',
            value: '24,521',
            change: '+12.4%',
            changeType: 'up' as const,
            icon: <Users size={18} className="text-white" />,
            color: 'bg-indigo-500/20',
        },
        {
            title: 'Monthly Revenue',
            value: '$89,430',
            change: '+8.7%',
            changeType: 'up' as const,
            icon: <DollarSign size={18} className="text-white" />,
            color: 'bg-emerald-500/20',
        },
        {
            title: 'Active Sessions',
            value: '3,842',
            change: '-2.1%',
            changeType: 'down' as const,
            icon: <Activity size={18} className="text-white" />,
            color: 'bg-amber-500/20',
        },
        {
            title: 'Engagement Rate',
            value: '73.6%',
            change: '+5.3%',
            changeType: 'up' as const,
            icon: <BarChart3 size={18} className="text-white" />,
            color: 'bg-purple-500/20',
        },
    ]

    return (
        <div className="min-h-screen bg-gray-950 p-8">
            <div className="max-w-7xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <h1 className="text-3xl font-bold text-white">Stats Overview</h1>
                    <p className="text-gray-400 mt-1">Key metrics and performance indicators</p>
                </motion.div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    {stats.map((stat, i) => (
                        <motion.div key={stat.title} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
                            <StatCard {...stat} />
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    )
}
