import React from 'react'
import { motion } from 'framer-motion'
import { Bell, Shield, Users, BarChart3, CheckCircle } from 'lucide-react'

const notifications = [
    { icon: <Users size={15} className="text-indigo-400" />, bg: 'bg-indigo-500/10', title: 'New user registered', desc: 'Eva Patel joined the platform', time: '2 min ago', unread: true },
    { icon: <Shield size={15} className="text-emerald-400" />, bg: 'bg-emerald-500/10', title: 'Security alert', desc: 'Login from new device detected', time: '18 min ago', unread: true },
    { icon: <BarChart3 size={15} className="text-amber-400" />, bg: 'bg-amber-500/10', title: 'Report ready', desc: 'Monthly analytics report is ready', time: '1 hr ago', unread: false },
    { icon: <CheckCircle size={15} className="text-purple-400" />, bg: 'bg-purple-500/10', title: 'Deployment success', desc: 'v2.4.1 deployed to production', time: '3 hr ago', unread: false },
    { icon: <Bell size={15} className="text-gray-400" />, bg: 'bg-gray-500/10', title: 'System maintenance', desc: 'Scheduled maintenance in 48 hours', time: '1 day ago', unread: false },
]

export default function Notifications() {
    return (
        <div className="min-h-screen bg-gray-950 p-8">
            <div className="max-w-2xl mx-auto">
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Notifications</h1>
                        <p className="text-gray-400 mt-1">Stay up to date with your platform activity</p>
                    </div>
                    <button className="text-indigo-400 text-sm hover:text-indigo-300 transition-colors">Mark all read</button>
                </motion.div>

                <div className="space-y-3">
                    {notifications.map((n, i) => (
                        <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.07 }}
                            className={`flex items-start gap-4 p-4 rounded-2xl border transition-colors cursor-pointer
                ${n.unread ? 'bg-gray-900 border-indigo-500/20 hover:border-indigo-500/40' : 'bg-gray-900/50 border-white/5 hover:border-white/10'}`}>
                            <div className={`w-9 h-9 rounded-xl ${n.bg} flex items-center justify-center shrink-0 mt-0.5`}>
                                {n.icon}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                    <p className="text-white text-sm font-medium">{n.title}</p>
                                    {n.unread && <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0" />}
                                </div>
                                <p className="text-gray-500 text-xs mt-0.5">{n.desc}</p>
                            </div>
                            <span className="text-gray-600 text-xs whitespace-nowrap">{n.time}</span>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    )
}
