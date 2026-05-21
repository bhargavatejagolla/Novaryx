'use client';

import { motion } from 'framer-motion';
import { Palette, Bell, Shield, Database, Globe, Sliders } from 'lucide-react';
import { ThemeCustomizer } from '@/components/ui/ThemeCustomizer';
import { useTheme } from '@/hooks/useTheme';
import { useState } from 'react';

type SettingsTab = 'appearance' | 'preferences' | 'advanced';

export default function SettingsPage() {
    const { theme, setTheme, toggleMode } = useTheme();
    const [activeTab, setActiveTab] = useState<SettingsTab>('appearance');

    const tabs: { id: SettingsTab; label: string; icon: any }[] = [
        { id: 'appearance', label: 'Appearance', icon: Palette },
        { id: 'preferences', label: 'Preferences', icon: Sliders },
        { id: 'advanced', label: 'Advanced', icon: Shield },
    ];

    return (
        <div className="max-w-4xl mx-auto px-6 py-8">
            <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold">Settings</h1>
                <p className="text-gray-500 mt-2">Customize your NOVARYX experience</p>
            </motion.div>

            <div className="flex gap-6">
                {/* Sidebar */}
                <div className="w-56 flex-shrink-0 space-y-1">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === tab.id
                                    ? 'bg-[var(--primary)]/10 text-[var(--primary)]'
                                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <tab.icon className="w-4 h-4" />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="flex-1">
                    {activeTab === 'appearance' && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="glass rounded-2xl p-8"
                        >
                            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                                <Palette className="w-5 h-5 text-[var(--primary)]" />
                                Appearance
                            </h2>
                            <ThemeCustomizer
                                theme={theme}
                                onThemeChange={setTheme}
                                onToggleMode={toggleMode}
                            />
                        </motion.div>
                    )}

                    {activeTab === 'preferences' && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="glass rounded-2xl p-8"
                        >
                            <h2 className="text-xl font-semibold mb-6">Generation Preferences</h2>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm text-gray-400 mb-2 block">Default Project Type</label>
                                    <select className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white">
                                        <option value="saas_dashboard">SaaS Dashboard</option>
                                        <option value="landing_page">Landing Page</option>
                                        <option value="ecommerce">E-Commerce</option>
                                        <option value="admin_panel">Admin Panel</option>
                                        <option value="portfolio">Portfolio</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="text-sm text-gray-400 mb-2 block">Default Complexity</label>
                                    <select className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white">
                                        <option value="simple">Simple</option>
                                        <option value="medium">Medium</option>
                                        <option value="complex">Complex</option>
                                    </select>
                                </div>
                                <div className="flex items-center justify-between py-2">
                                    <span className="text-sm text-gray-400">Auto-export ZIP</span>
                                    <button className="w-11 h-6 rounded-full bg-white/10 relative">
                                        <div className="w-4 h-4 rounded-full bg-white absolute top-1 left-1" />
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {activeTab === 'advanced' && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="glass rounded-2xl p-8"
                        >
                            <h2 className="text-xl font-semibold mb-6">Advanced Settings</h2>
                            <div className="space-y-4">
                                <div className="p-4 rounded-xl bg-yellow-500/5 border border-yellow-500/10">
                                    <p className="text-sm text-yellow-400">
                                        ⚠️ These settings affect system behavior. Change with caution.
                                    </p>
                                </div>
                                <div>
                                    <label className="text-sm text-gray-400 mb-2 block">LLM Model</label>
                                    <select className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white">
                                        <option>qwen2.5-coder:7b</option>
                                        <option>deepseek-coder:6.7b</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="text-sm text-gray-400 mb-2 block">Max Parallel Agents</label>
                                    <input type="number" defaultValue={3} min={1} max={6} className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white" />
                                </div>
                                <button className="px-4 py-2 rounded-xl bg-red-500/10 text-red-400 text-sm font-medium hover:bg-red-500/20 transition-colors">
                                    Clear Memory Store
                                </button>
                            </div>
                        </motion.div>
                    )}
                </div>
            </div>
        </div>
    );
}