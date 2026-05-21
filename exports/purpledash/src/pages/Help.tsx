import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, ChevronDown, ChevronRight, Book, Zap, Shield, Users, BarChart3, MessageCircle } from 'lucide-react'

const faqs = [
    { q: 'How do I invite team members?', a: 'Go to User Management and click "Invite User". Enter their email and select a role. They will receive an invitation email.' },
    { q: 'How do I generate an analytics report?', a: 'Navigate to Analytics, select your date range, and click Export. Reports are available in CSV and PDF format.' },
    { q: 'Can I customize the dashboard layout?', a: 'Yes! Use the drag handles on each widget to rearrange them. Click the settings icon on any widget to configure it.' },
    { q: 'How do I reset a user\'s password?', a: 'In User Management, click the Actions menu next to a user and select "Reset Password". They\'ll receive a reset email.' },
]

const docs = [
    { icon: <Book size={16} />, title: 'Getting Started', desc: 'Set up your workspace in minutes', color: 'text-indigo-400', bg: 'bg-indigo-500/10' },
    { icon: <Zap size={16} />, title: 'API Reference', desc: 'Full REST API documentation', color: 'text-amber-400', bg: 'bg-amber-500/10' },
    { icon: <Shield size={16} />, title: 'Security Guide', desc: 'Best practices for securing your account', color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { icon: <BarChart3 size={16} />, title: 'Analytics Docs', desc: 'Deep dive into metrics and reporting', color: 'text-purple-400', bg: 'bg-purple-500/10' },
]

export default function Help() {
    const [open, setOpen] = useState<number | null>(null)

    return (
        <div className="min-h-screen bg-gray-950 p-8">
            <div className="max-w-2xl mx-auto space-y-8">
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                    <h1 className="text-3xl font-bold text-white">Help Center</h1>
                    <p className="text-gray-400 mt-1">Find answers and get support</p>
                </motion.div>

                {/* Search */}
                <div className="relative">
                    <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
                    <input placeholder="Search docs, FAQs..." className="w-full bg-gray-900 border border-white/5 rounded-xl pl-11 pr-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-indigo-500/50 transition-colors" />
                </div>

                {/* Docs grid */}
                <div className="grid grid-cols-2 gap-4">
                    {docs.map((d, i) => (
                        <motion.button key={d.title} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
                            whileHover={{ scale: 1.02 }} className="text-left p-4 bg-gray-900 border border-white/5 rounded-2xl hover:border-white/10 transition-all">
                            <div className={`w-9 h-9 rounded-xl ${d.bg} flex items-center justify-center ${d.color} mb-3`}>{d.icon}</div>
                            <p className="text-white text-sm font-medium">{d.title}</p>
                            <p className="text-gray-500 text-xs mt-0.5">{d.desc}</p>
                        </motion.button>
                    ))}
                </div>

                {/* FAQs */}
                <div>
                    <h2 className="text-white font-semibold mb-4">Frequently Asked Questions</h2>
                    <div className="space-y-2">
                        {faqs.map((f, i) => (
                            <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 + i * 0.07 }}
                                className="bg-gray-900 border border-white/5 rounded-xl overflow-hidden">
                                <button onClick={() => setOpen(open === i ? null : i)}
                                    className="w-full flex items-center justify-between p-4 text-left hover:bg-white/[0.02] transition-colors">
                                    <span className="text-white text-sm font-medium">{f.q}</span>
                                    <motion.div animate={{ rotate: open === i ? 180 : 0 }} transition={{ duration: 0.2 }}>
                                        <ChevronDown size={15} className="text-gray-600" />
                                    </motion.div>
                                </button>
                                {open === i && (
                                    <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} className="px-4 pb-4">
                                        <p className="text-gray-400 text-sm">{f.a}</p>
                                    </motion.div>
                                )}
                            </motion.div>
                        ))}
                    </div>
                </div>

                {/* Contact */}
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}
                    className="flex items-center gap-4 p-5 bg-indigo-600/10 border border-indigo-500/20 rounded-2xl">
                    <MessageCircle size={20} className="text-indigo-400 shrink-0" />
                    <div className="flex-1">
                        <p className="text-white text-sm font-medium">Still need help?</p>
                        <p className="text-gray-400 text-xs mt-0.5">Chat with our support team</p>
                    </div>
                    <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-xl transition-colors">Start Chat</button>
                </motion.div>
            </div>
        </div>
    )
}
