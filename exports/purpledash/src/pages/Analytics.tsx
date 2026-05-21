import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, TrendingUp, Users, Globe, Calendar, Download } from 'lucide-react'

const metrics = [
    { label: 'Page Views', value: '1.2M', trend: '+18%', color: 'bg-indigo-500' },
    { label: 'Unique Visitors', value: '340K', trend: '+11%', color: 'bg-purple-500' },
    { label: 'Avg. Session', value: '4m 22s', trend: '+5%', color: 'bg-emerald-500' },
    { label: 'Bounce Rate', value: '38.2%', trend: '-3%', color: 'bg-amber-500' },
]

const channels = [
    { name: 'Organic Search', pct: 42, color: 'bg-indigo-500' },
    { name: 'Direct', pct: 28, color: 'bg-purple-500' },
    { name: 'Social Media', pct: 18, color: 'bg-emerald-500' },
    { name: 'Referral', pct: 12, color: 'bg-amber-500' },
]

export default function Analytics() {
    const [period, setPeriod] = useState('7d')

    return (
        <div className="min-h-screen bg-gray-950 p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Analytics</h1>
                        <p className="text-gray-400 mt-1">Deep insights into your platform performance</p>
                    </div>
                    <div className="flex items-center gap-2">
                        {['24h', '7d', '30d', '90d'].map(p => (
                            <button
                                key={p}
                                onClick={() => setPeriod(p)}
                                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${period === p ? 'bg-indigo-600 text-white' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
                            >
                                {p}
                            </button>
                        ))}
                        <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 border border-white/5 rounded-lg text-gray-400 text-xs hover:text-white transition-colors ml-2">
                            <Download size={13} /> Export
                        </button>
                    </div>
                </motion.div>

                {/* Metric cards */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
                    {metrics.map((m, i) => (
                        <motion.div key={m.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
                            className="bg-gray-900 border border-white/5 rounded-2xl p-5">
                            <div className={`w-2 h-2 rounded-full ${m.color} mb-3`} />
                            <p className="text-gray-500 text-sm">{m.label}</p>
                            <p className="text-2xl font-bold text-white mt-1">{m.value}</p>
                            <p className="text-emerald-400 text-xs mt-1 font-medium">{m.trend} vs prev period</p>
                        </motion.div>
                    ))}
                </div>

                {/* Chart placeholder + channels */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
                        className="lg:col-span-2 bg-gray-900 border border-white/5 rounded-2xl p-6 h-72 flex flex-col">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-white font-semibold">Traffic Overview</h2>
                            <BarChart3 size={16} className="text-gray-600" />
                        </div>
                        <div className="flex-1 flex items-end gap-2">
                            {[40, 65, 50, 80, 55, 90, 72, 85, 60, 95, 70, 88, 75, 92].map((h, i) => (
                                <motion.div key={i} initial={{ scaleY: 0 }} animate={{ scaleY: 1 }} transition={{ delay: 0.35 + i * 0.04, origin: 'bottom' }}
                                    style={{ height: `${h}%` }} className="flex-1 bg-indigo-500/30 hover:bg-indigo-500/60 rounded-t-md transition-colors cursor-pointer" />
                            ))}
                        </div>
                    </motion.div>

                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.35 }}
                        className="bg-gray-900 border border-white/5 rounded-2xl p-6">
                        <h2 className="text-white font-semibold mb-5">Traffic Sources</h2>
                        <div className="space-y-4">
                            {channels.map((c, i) => (
                                <div key={c.name}>
                                    <div className="flex justify-between text-xs mb-1.5">
                                        <span className="text-gray-400">{c.name}</span>
                                        <span className="text-white font-medium">{c.pct}%</span>
                                    </div>
                                    <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                                        <motion.div initial={{ width: 0 }} animate={{ width: `${c.pct}%` }} transition={{ delay: 0.4 + i * 0.1, duration: 0.6 }}
                                            className={`h-full ${c.color} rounded-full`} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                </div>
            </div>
        </div>
    )
}
