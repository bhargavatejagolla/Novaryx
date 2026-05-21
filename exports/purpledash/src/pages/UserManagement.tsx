import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Plus, MoreHorizontal, Shield, User, Trash2, Edit3, ChevronDown } from 'lucide-react'

interface UserRecord {
    id: number
    name: string
    email: string
    role: 'Admin' | 'Moderator' | 'Member' | 'Viewer'
    status: 'active' | 'inactive'
    avatar: string
    joined: string
}

const ROLE_COLORS: Record<string, string> = {
    Admin: 'bg-red-500/20 text-red-400 border-red-500/30',
    Moderator: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    Member: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
    Viewer: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

export default function UserManagement() {
    const [search, setSearch] = useState('')
    const [users] = useState<UserRecord[]>([
        { id: 1, name: 'Alice Chen', email: 'alice@company.io', role: 'Admin', status: 'active', avatar: 'AC', joined: 'Jan 2024' },
        { id: 2, name: 'Bob Martinez', email: 'bob@company.io', role: 'Moderator', status: 'active', avatar: 'BM', joined: 'Feb 2024' },
        { id: 3, name: 'Carol Kim', email: 'carol@company.io', role: 'Member', status: 'inactive', avatar: 'CK', joined: 'Mar 2024' },
        { id: 4, name: 'David Lee', email: 'david@company.io', role: 'Viewer', status: 'active', avatar: 'DL', joined: 'Apr 2024' },
        { id: 5, name: 'Eva Patel', email: 'eva@company.io', role: 'Member', status: 'active', avatar: 'EP', joined: 'May 2024' },
    ])

    const filtered = users.filter(
        u => u.name.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase())
    )

    return (
        <div className="min-h-screen bg-gray-950 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-white">User Management</h1>
                        <p className="text-gray-400 mt-1">Manage access, roles and permissions</p>
                    </div>
                    <motion.button
                        whileHover={{ scale: 1.04 }}
                        whileTap={{ scale: 0.97 }}
                        className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium text-sm transition-colors"
                    >
                        <Plus size={16} />
                        Invite User
                    </motion.button>
                </motion.div>

                {/* Search */}
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="relative mb-6">
                    <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
                    <input
                        type="text"
                        placeholder="Search users..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        className="w-full bg-gray-900 border border-white/5 rounded-xl pl-11 pr-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-indigo-500/50 transition-colors"
                    />
                </motion.div>

                {/* Table */}
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="bg-gray-900 border border-white/5 rounded-2xl overflow-hidden">
                    <div className="grid grid-cols-[1fr_auto_auto_auto] items-center px-6 py-3 border-b border-white/5 text-xs text-gray-500 uppercase tracking-wider">
                        <span>User</span>
                        <span className="w-28 text-center">Role</span>
                        <span className="w-20 text-center">Status</span>
                        <span className="w-16 text-center">Actions</span>
                    </div>

                    <AnimatePresence>
                        {filtered.map((user, i) => (
                            <motion.div
                                key={user.id}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                transition={{ delay: i * 0.05 }}
                                className="grid grid-cols-[1fr_auto_auto_auto] items-center px-6 py-4 border-b border-white/5 last:border-0 hover:bg-white/[0.02] transition-colors"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-9 h-9 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-semibold text-sm">
                                        {user.avatar}
                                    </div>
                                    <div>
                                        <p className="text-white text-sm font-medium">{user.name}</p>
                                        <p className="text-gray-500 text-xs">{user.email}</p>
                                    </div>
                                </div>

                                <div className="w-28 flex justify-center">
                                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${ROLE_COLORS[user.role]}`}>
                                        {user.role}
                                    </span>
                                </div>

                                <div className="w-20 flex justify-center">
                                    <span className={`flex items-center gap-1 text-xs font-medium ${user.status === 'active' ? 'text-emerald-400' : 'text-gray-500'}`}>
                                        <span className={`w-1.5 h-1.5 rounded-full ${user.status === 'active' ? 'bg-emerald-400' : 'bg-gray-600'}`} />
                                        {user.status}
                                    </span>
                                </div>

                                <div className="w-16 flex justify-center gap-1">
                                    <button className="p-1.5 text-gray-600 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                                        <Edit3 size={14} />
                                    </button>
                                    <button className="p-1.5 text-gray-600 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors">
                                        <Trash2 size={14} />
                                    </button>
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </motion.div>
            </div>
        </div>
    )
}
