'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Wand2, FolderOpen, Clock, TrendingUp, ArrowRight } from 'lucide-react';
import { PromptInput } from '@/components/ui/PromptInput';
import { GenerationProgress } from '@/components/ui/GenerationProgress';
import { ProjectCard } from '@/components/ui/ProjectCard';
import { useGeneration } from '@/hooks/useGeneration';
import { getProjects } from '@/lib/api';
import Link from 'next/link';

export default function DashboardPage() {
    const generation = useGeneration();
    const [recentProjects, setRecentProjects] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = async () => {
        try {
            const data = await getProjects();
            setRecentProjects(data?.projects || []);
        } catch (err) {
            console.error('Failed to load projects:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerate = async (prompt: string) => {
        await generation.generate(prompt);
        loadProjects();
    };

    return (
        <div className="max-w-7xl mx-auto px-6 py-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <p className="text-gray-500 mt-2">Generate and manage your projects</p>
            </motion.div>

            {/* Quick Generate */}
            <div className="mb-10">
                <PromptInput onSubmit={handleGenerate} loading={generation.status === 'generating'} />
            </div>

            {/* Generation Progress */}
            {generation.status !== 'idle' && (
                <div className="mb-10">
                    <GenerationProgress {...generation} />
                </div>
            )}

            {/* Stats Row */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
                {[
                    { icon: FolderOpen, label: 'Total Projects', value: recentProjects.length.toString(), color: 'text-[var(--primary)]' },
                    { icon: Clock, label: 'Last Generated', value: recentProjects[0]?.name?.slice(0, 12) || '—', color: 'text-accent' },
                    { icon: TrendingUp, label: 'Success Rate', value: '100%', color: 'text-green-400' },
                ].map((stat, i) => (
                    <div key={i} className="glass-card p-5 rounded-2xl flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center">
                            <stat.icon className={`w-5 h-5 ${stat.color}`} />
                        </div>
                        <div>
                            <div className="text-2xl font-bold">{stat.value}</div>
                            <div className="text-xs text-gray-500">{stat.label}</div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Recent Projects */}
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold">Recent Projects</h2>
                <Link
                    href="/gallery"
                    className="text-sm text-[var(--primary)] hover:underline flex items-center gap-1"
                >
                    View All <ArrowRight className="w-3 h-3" />
                </Link>
            </div>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="rounded-2xl bg-white/5 h-48 animate-pulse" />
                    ))}
                </div>
            ) : recentProjects.length === 0 ? (
                <div className="text-center py-16 glass rounded-2xl">
                    <Wand2 className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-500">No projects yet. Generate your first one!</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {recentProjects.slice(0, 6).map((project, i) => (
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