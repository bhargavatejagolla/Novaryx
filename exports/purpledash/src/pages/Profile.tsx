import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Camera, MapPin, Link2, Twitter, Github, Save } from 'lucide-react'

export default function Profile() {
    const [saved, setSaved] = useState(false)

    return (
        <div className="min-h-screen bg-gray-950 p-8">
            <div className="max-w-2xl mx-auto">
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                    <h1 className="text-3xl font-bold text-white">Profile</h1>
                    <p className="text-gray-400 mt-1">Manage your public profile information</p>
                </motion.div>

                {/* Avatar */}
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
                    className="flex items-center gap-6 bg-gray-900 border border-white/5 rounded-2xl p-6 mb-6">
                    <div className="relative">
                        <div className="w-20 h-20 rounded-2xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 text-3xl font-bold">
                            AC
                        </div>
                        <button className="absolute -bottom-1 -right-1 w-7 h-7 bg-indigo-600 hover:bg-indigo-500 rounded-full flex items-center justify-center transition-colors">
                            <Camera size={12} className="text-white" />
                        </button>
                    </div>
                    <div>
                        <p className="text-white font-semibold text-lg">Alice Chen</p>
                        <p className="text-gray-500 text-sm">Administrator · Joined Jan 2024</p>
                        <div className="flex items-center gap-2 mt-2">
                            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Active</span>
                            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">Admin</span>
                        </div>
                    </div>
                </motion.div>

                {/* Details */}
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
                    className="bg-gray-900 border border-white/5 rounded-2xl p-6 space-y-5">
                    <div className="grid grid-cols-2 gap-4">
                        {[['First Name', 'Alice'], ['Last Name', 'Chen']].map(([l, v]) => (
                            <div key={l}>
                                <label className="text-gray-500 text-xs mb-1.5 block">{l}</label>
                                <input defaultValue={v} className="w-full bg-gray-800 border border-white/5 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500/50 transition-colors" />
                            </div>
                        ))}
                    </div>
                    <div>
                        <label className="text-gray-500 text-xs mb-1.5 block">Bio</label>
                        <textarea defaultValue="Full-stack developer & platform admin. Building great products." rows={3}
                            className="w-full bg-gray-800 border border-white/5 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500/50 transition-colors resize-none" />
                    </div>
                    {[
                        { icon: <MapPin size={14} />, label: 'Location', val: 'San Francisco, CA' },
                        { icon: <Link2 size={14} />, label: 'Website', val: 'https://alice.dev' },
                        { icon: <Twitter size={14} />, label: 'Twitter', val: '@alice_chen' },
                        { icon: <Github size={14} />, label: 'GitHub', val: 'alice-chen' },
                    ].map(f => (
                        <div key={f.label}>
                            <label className="text-gray-500 text-xs mb-1.5 block">{f.label}</label>
                            <div className="relative">
                                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600">{f.icon}</span>
                                <input defaultValue={f.val} className="w-full bg-gray-800 border border-white/5 rounded-xl pl-9 pr-4 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500/50 transition-colors" />
                            </div>
                        </div>
                    ))}
                    <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                        onClick={() => { setSaved(true); setTimeout(() => setSaved(false), 2000) }}
                        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium ${saved ? 'bg-emerald-600' : 'bg-indigo-600 hover:bg-indigo-500'} text-white transition-colors`}>
                        <Save size={15} /> {saved ? 'Saved!' : 'Save Profile'}
                    </motion.button>
                </motion.div>
            </div>
        </div>
    )
}
