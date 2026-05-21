import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Mail, Lock, Bell, Palette, Shield, Save } from 'lucide-react'

const tabs = ['General', 'Security', 'Notifications', 'Appearance']

export default function Settings() {
    const [active, setActive] = useState('General')
    const [saved, setSaved] = useState(false)

    const handleSave = () => {
        setSaved(true)
        setTimeout(() => setSaved(false), 2000)
    }

    return (
        <div className="min-h-screen bg-gray-950 p-8">
            <div className="max-w-3xl mx-auto">
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                    <h1 className="text-3xl font-bold text-white">Settings</h1>
                    <p className="text-gray-400 mt-1">Manage your account and preferences</p>
                </motion.div>

                {/* Tabs */}
                <div className="flex gap-1 bg-gray-900/50 p-1 rounded-xl mb-8 border border-white/5">
                    {tabs.map(t => (
                        <button key={t} onClick={() => setActive(t)}
                            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${active === t ? 'bg-gray-800 text-white shadow-sm' : 'text-gray-500 hover:text-gray-300'}`}>
                            {t}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <motion.div key={active} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}
                    className="bg-gray-900 border border-white/5 rounded-2xl p-6 space-y-6">

                    {active === 'General' && (
                        <>
                            <Field icon={<User size={15} />} label="Full Name" defaultValue="Alice Chen" />
                            <Field icon={<Mail size={15} />} label="Email" defaultValue="alice@company.io" type="email" />
                            <Field icon={<User size={15} />} label="Username" defaultValue="@alice.chen" />
                        </>
                    )}

                    {active === 'Security' && (
                        <>
                            <Field icon={<Lock size={15} />} label="Current Password" type="password" defaultValue="••••••••" />
                            <Field icon={<Lock size={15} />} label="New Password" type="password" defaultValue="" />
                            <Field icon={<Lock size={15} />} label="Confirm Password" type="password" defaultValue="" />
                            <div className="flex items-center justify-between p-4 bg-gray-800 rounded-xl">
                                <div>
                                    <p className="text-white text-sm font-medium">Two-Factor Authentication</p>
                                    <p className="text-gray-500 text-xs mt-0.5">Add an extra layer of security</p>
                                </div>
                                <div className="w-10 h-5 bg-indigo-600 rounded-full flex items-center px-0.5 cursor-pointer">
                                    <div className="w-4 h-4 bg-white rounded-full ml-auto" />
                                </div>
                            </div>
                        </>
                    )}

                    {active === 'Notifications' && (
                        <>
                            {['Email Notifications', 'Push Notifications', 'Weekly Reports', 'Security Alerts'].map(n => (
                                <div key={n} className="flex items-center justify-between p-4 bg-gray-800 rounded-xl">
                                    <p className="text-white text-sm">{n}</p>
                                    <div className="w-10 h-5 bg-indigo-600 rounded-full flex items-center px-0.5 cursor-pointer">
                                        <div className="w-4 h-4 bg-white rounded-full ml-auto" />
                                    </div>
                                </div>
                            ))}
                        </>
                    )}

                    {active === 'Appearance' && (
                        <>
                            <div>
                                <p className="text-gray-400 text-sm mb-3">Theme</p>
                                <div className="flex gap-3">
                                    {['Dark', 'Light', 'System'].map(t => (
                                        <button key={t} className={`flex-1 py-3 rounded-xl border text-sm font-medium transition-all ${t === 'Dark' ? 'border-indigo-500 text-white bg-indigo-500/10' : 'border-white/5 text-gray-500 hover:text-white hover:border-white/20'}`}>
                                            {t}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <p className="text-gray-400 text-sm mb-3">Accent Color</p>
                                <div className="flex gap-3">
                                    {['#6366f1', '#8b5cf6', '#ec4899', '#14b8a6', '#f59e0b'].map(c => (
                                        <button key={c} style={{ background: c }} className="w-8 h-8 rounded-full border-2 border-white/20 hover:border-white/60 transition-all" />
                                    ))}
                                </div>
                            </div>
                        </>
                    )}

                    <div className="pt-2">
                        <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={handleSave}
                            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-colors ${saved ? 'bg-emerald-600 text-white' : 'bg-indigo-600 hover:bg-indigo-500 text-white'}`}>
                            <Save size={15} />
                            {saved ? 'Saved!' : 'Save Changes'}
                        </motion.button>
                    </div>
                </motion.div>
            </div>
        </div>
    )
}

function Field({ icon, label, defaultValue, type = 'text' }: { icon: React.ReactNode; label: string; defaultValue: string; type?: string }) {
    return (
        <div>
            <label className="text-gray-400 text-xs mb-1.5 block">{label}</label>
            <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600">{icon}</span>
                <input type={type} defaultValue={defaultValue}
                    className="w-full bg-gray-800 border border-white/5 rounded-xl pl-9 pr-4 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500/50 transition-colors" />
            </div>
        </div>
    )
}
