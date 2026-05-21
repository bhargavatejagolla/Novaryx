'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Sparkles } from 'lucide-react';
import { ProjectCard } from '@/components/ui/ProjectCard';
import { getProjects } from '@/lib/api';
import Link from 'next/link';

export default function GalleryPage() {
    const [projects, setProjects] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = async () => {
        try {
            const data = await getProjects();
            setProjects(data?.projects || []);
        } catch (err) {
            console.error('Failed to load projects:', err);
        } finally {
            setLoading(false);
        }
    };

    const filtered = projects.filter((p) => {
        const matchesSearch = p.name?.toLowerCase().includes(search.toLowerCase()) ||
            p.type?.toLowerCase().includes(search.toLowerCase());
        const matchesFilter = filter === 'all' || p.type === filter;
        return matchesSearch && matchesFilter;
    });

    const types = ['all', ...Array.from(new Set(projects.map((p) => p.type).filter(Boolean)))];

    return (
        <div className="max-w-7xl mx-auto px-6 py-8">
            <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold">Project Gallery</h1>
                <p className="text-gray-500 mt-2">Browse all generated projects</p>
            </motion.div>

            {/* Search & Filter */}
            <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <div className="flex-1 relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search projects..."
                        className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:border-[var(--primary)] outline-none transition-colors"
                    />
                </div>
                <div className="flex gap-2 flex-wrap">
                    {types.map((type) => (
                        <button
                            key={type}
                            onClick={() => setFilter(type)}
                            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${filter === type
                                    ? 'bg-[var(--primary)] text-white'
                                    : 'bg-white/5 text-gray-400 hover:text-white'
                                }`}
                        >
                            {type === 'all' ? 'All' : type.replace('_', ' ')}
                        </button>
                    ))}
                </div>
            </div>

            {/* Grid */}
            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div key={i} className="rounded-2xl bg-white/5 h-48 animate-pulse" />
                    ))}
                </div>
            ) : filtered.length === 0 ? (
                <div className="text-center py-20 glass rounded-2xl">
                    <Sparkles className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold mb-2">No projects found</h3>
                    <p className="text-gray-500 mb-6">
                        {search ? 'Try a different search term' : 'Generate your first project'}
                    </p>
                    <Link
                        href="/builder"
                        className="px-6 py-3 rounded-xl bg-[var(--primary)] text-white font-medium hover:shadow-[0_0_25px_rgba(99,102,241,0.4)] transition-shadow inline-flex items-center gap-2"
                    >
                        <Sparkles className="w-4 h-4" />
                        Generate Project
                    </Link>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filtered.map((project, i) => (
                        <ProjectCard
                            key={i}
                            project={project}
                            onClick={() => window.location.href = `/export?id=${project.id}`}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}