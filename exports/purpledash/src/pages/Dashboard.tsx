import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, Users, DollarSign, Activity, ArrowUpRight, Bell } from 'lucide-react'

const stats = [
    { label: 'Total Revenue', value: '$124,560', change: '+14.2%', icon: DollarSign, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { label: 'Active Users', value: '8,342', change: '+6.1%', icon: Users, color: 'text-indigo-400', bg: 'bg-indigo-500/10' },
    { label: 'Growth Rate', value: '23.4%', change: '+2.8%', icon: TrendingUp, color: 'text-amber-400', bg: 'bg-amber-500/10' },
    { label: 'Uptime', value: '99.98%', change: '+0.1%', icon: Activity, color: 'text-purple-400', bg: 'bg-purple-500/10' },
]

const recentActivity = [
    { user: 'Alice Chen', action: 'Created new project', time: '2 min ago', avatar: 'AC' },
    { user: 'Bob Martinez', action: 'Updated user permissions', time: '15 min ago', avatar: 'BM' },
    { user: 'Carol Kim', action: 'Deployed to production', time: '1 hr ago', avatar: 'CK' },
    { user: 'David Lee', action: 'Invited 3 team members', time: '3 hr ago', avatar: 'DL' },
    { user: 'Eva Patel', action: 'Generated analytics report', time: '5 hr ago', avatar: 'EP' },
]

export default function Dashboard() {
    return (
        <div className="min-h-screen bg-gray-950 p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                    <h1 className="text-3xl font-bold text-white">Good morning 👋</h1>
                    <p className="text-gray-400 mt-1">Here's what's happening with your platform today.</p>
                </motion.div>

                {/* Stats grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                    {stats.map((s, i) => (
                        <motion.div
                            key={s.label}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.08 }}
                            whileHover={{ scale: 1.02 }}
                            className="bg-gray-900 border border-white/5 rounded-2xl p-5 hover:border-white/10 transition-all"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <span className="text-gray-500 text-sm">{s.label}</span>
                                <div className={`w-9 h-9 rounded-xl ${s.bg} flex items-center justify-center`}>
                                    <s.icon size={16} className={s.color} />
                                </div>
                            </div>
                            <p className="text-2xl font-bold text-white">{s.value}</p>
                            <div className="flex items-center gap-1 mt-1">
                                <ArrowUpRight size={13} className="text-emerald-400" />
                                <span className="text-emerald-400 text-xs font-medium">{s.change}</span>
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Activity feed */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="bg-gray-900 border border-white/5 rounded-2xl p-6">
                        <div className="flex items-center justify-between mb-5">
                            <h2 className="text-white font-semibold">Recent Activity</h2>
                            <Bell size={15} className="text-gray-600" />
                        </div>
                        <div className="space-y-4">
                            {recentActivity.map((a, i) => (
                                <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 + i * 0.07 }} className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 text-xs font-bold shrink-0">
                                        {a.avatar}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-white text-sm font-medium truncate">{a.user}</p>
                                        <p className="text-gray-500 text-xs truncate">{a.action}</p>
                                    </div>
                                    <span className="text-gray-600 text-xs whitespace-nowrap">{a.time}</span>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>

                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="bg-gray-900 border border-white/5 rounded-2xl p-6">
                        <h2 className="text-white font-semibold mb-5">Quick Actions</h2>
                        <div className="grid grid-cols-2 gap-3">
                            {['Invite User', 'Generate Report', 'View Analytics', 'Manage Roles', 'Export Data', 'Deploy Update'].map((action, i) => (
                                <motion.button
                                    key={action}
                                    whileHover={{ scale: 1.03 }}
                                    whileTap={{ scale: 0.97 }}
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: 0.4 + i * 0.05 }}
                                    className="p-3 bg-gray-800 hover:bg-gray-700 border border-white/5 rounded-xl text-gray-300 text-sm font-medium text-left transition-colors"
                                >
                                    {action}
                                </motion.button>
                            ))}
                        </div>
                    </motion.div>
                </div>
            </div>
        </div>
    )
}
