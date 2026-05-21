'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, History, ArrowRight, Code2, Layers, Cpu, Zap } from 'lucide-react';
import { PromptInput } from '@/components/ui/PromptInput';
import { GenerationProgress } from '@/components/ui/GenerationProgress';
import { useOrchestratorStream } from '@/hooks/useOrchestratorStream';
import { useOrchestrationStore } from '@/store/useOrchestrationStore';
import { EXAMPLE_PROMPTS } from '@/lib/constants';

export default function HomePage() {
    const router = useRouter();
    const generationStream = useOrchestratorStream();
    const store = useOrchestrationStore();
    const [recentJobs, setRecentJobs] = useState<any[]>([]);
    const [showHistory, setShowHistory] = useState(false);

    useEffect(() => {
        fetch('/api/projects')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    setRecentJobs(data.jobs.slice(0, 5));
                }
            })
            .catch(console.error);
    }, []);

    const handleGenerate = (prompt: string) => {
        generationStream.generate(prompt).catch(err => console.error('Generation failed:', err));
        router.push('/builder');
    };

    return (
        <div className="min-h-screen selection:bg-indigo-500/30">
            {/* Header */}
            <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-[#030712]/80 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                            <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        NOVARYX
                    </div>
                    <button
                        onClick={() => setShowHistory(!showHistory)}
                        className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/5 transition-colors text-sm font-medium text-gray-300"
                    >
                        <History className="w-4 h-4" />
                        Project History
                        {recentJobs.length > 0 && (
                            <span className="ml-1 px-1.5 py-0.5 rounded-md bg-indigo-500/20 text-indigo-400 text-xs">
                                {recentJobs.length}
                            </span>
                        )}
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <main className="relative pt-32 pb-20 px-6 max-w-5xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="text-center mb-16 relative z-10"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] uppercase font-bold mb-8 tracking-[0.2em] shadow-[0_0_20px_rgba(99,102,241,0.15)]">
                        <Cpu className="w-3.5 h-3.5" />
                        Next-Gen Orchestration Engine Active
                    </div>

                    <h1 className="text-5xl md:text-7xl font-semibold mb-6 tracking-tight leading-[1.1] text-white">
                        Architect Software.<br />
                        <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent filter drop-shadow-[0_0_30px_rgba(129,140,248,0.3)]">
                            Autonomous Generation.
                        </span>
                    </h1>

                    <p className="text-lg md:text-xl text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed font-light">
                        Describe your vision. NOVARYX will autonomously decompose the architecture, write the code, and assemble a production-ready application in seconds.
                    </p>
                </motion.div>

                {/* Prompt Input */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2, duration: 0.8 }}
                    className="max-w-3xl mx-auto"
                >
                    <div className="relative group mb-8">
                        <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200" />
                        <div className="relative">
                            <PromptInput onSubmit={handleGenerate} loading={store.status === 'generating'} />
                        </div>
                    </div>

                    {/* Quick Start Examples */}
                    {store.status === 'idle' && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.4 }}
                            className="mt-6"
                        >
                            <div className="flex items-center gap-2 text-sm text-gray-500 mb-4 px-2">
                                <Zap className="w-4 h-4 text-indigo-400" />
                                <span>Try these examples to start building instantly</span>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {EXAMPLE_PROMPTS.slice(0, 4).map((example, i) => (
                                    <button
                                        key={i}
                                        onClick={() => handleGenerate(example)}
                                        className="text-left p-4 rounded-xl bg-white/5 border border-white/5 hover:border-indigo-500/30 hover:bg-white/10 transition-all duration-200 group"
                                    >
                                        <p className="text-sm text-gray-400 group-hover:text-gray-300 line-clamp-2">
                                            "{example}"
                                        </p>
                                    </button>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </motion.div>

                {/* Generation Progress */}
                {store.status !== 'idle' && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="max-w-3xl mx-auto mt-12"
                    >
                        <GenerationProgress {...store} modules={Object.values(store.modules)} phase={store.globalPhase} progress={store.globalProgress} totalPhases={12} />
                    </motion.div>
                )}

                {/* Micro-Features (Replacing the bulky grid) */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5, duration: 1 }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto mt-24 border-t border-white/5 pt-12"
                >
                    <div className="text-center">
                        <div className="w-10 h-10 mx-auto rounded-full bg-white/5 flex items-center justify-center mb-4">
                            <Layers className="w-5 h-5 text-gray-400" />
                        </div>
                        <h3 className="text-white font-medium mb-2">Module Decomposition</h3>
                        <p className="text-sm text-gray-500">Intelligently breaks down prompts into dependency graphs.</p>
                    </div>
                    <div className="text-center">
                        <div className="w-10 h-10 mx-auto rounded-full bg-white/5 flex items-center justify-center mb-4">
                            <Code2 className="w-5 h-5 text-gray-400" />
                        </div>
                        <h3 className="text-white font-medium mb-2">Surgical Generation</h3>
                        <p className="text-sm text-gray-500">Generates isolated modules to prevent context overflow.</p>
                    </div>
                    <div className="text-center">
                        <div className="w-10 h-10 mx-auto rounded-full bg-white/5 flex items-center justify-center mb-4">
                            <Sparkles className="w-5 h-5 text-gray-400" />
                        </div>
                        <h3 className="text-white font-medium mb-2">Auto-Integration</h3>
                        <p className="text-sm text-gray-500">Seamlessly connects frontend, backend, and APIs.</p>
                    </div>
                </motion.div>
            </main>

            {/* History Drawer */}
            <AnimatePresence>
                {showHistory && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowHistory(false)}
                            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                        />
                        <motion.div
                            initial={{ x: '100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '100%' }}
                            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                            className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-[#0a0a0a] border-l border-white/10 z-50 p-6 shadow-2xl flex flex-col"
                        >
                            <div className="flex justify-between items-center mb-8">
                                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                    <History className="w-5 h-5 text-indigo-400" />
                                    Project History
                                </h2>
                                <button onClick={() => setShowHistory(false)} className="text-gray-400 hover:text-white">
                                    ✕
                                </button>
                            </div>

                            <div className="flex-1 overflow-y-auto pr-2 space-y-4 custom-scrollbar">
                                {recentJobs.length === 0 ? (
                                    <div className="text-center text-gray-500 mt-12">
                                        No recent projects found.
                                    </div>
                                ) : (
                                    recentJobs.map(job => (
                                        <div key={job.id} className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-indigo-500/30 transition-all duration-200 group flex flex-col gap-3">
                                            <div>
                                                <div className="flex justify-between items-center mb-1">
                                                    <h3 className="font-semibold text-white text-base group-hover:text-indigo-400 transition-colors">
                                                        {job.name || 'NOVARYX Project'}
                                                    </h3>
                                                    <span className="text-xs text-gray-500">
                                                        {new Date(job.timestamp).toLocaleDateString()}
                                                    </span>
                                                </div>
                                                <p className="text-xs text-gray-400 line-clamp-2 italic mb-2">
                                                    "{job.prompt || 'No prompt specified'}"
                                                </p>
                                                <div className="flex items-center justify-between text-xs pt-1 border-t border-white/5">
                                                    <span className="text-gray-500 font-mono">#{job.id}</span>
                                                    <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 font-medium capitalize">
                                                        {job.phase || 'completed'}
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="flex gap-2 mt-1">
                                                <button
                                                    onClick={() => {
                                                        if (job.phase === 'complete') {
                                                            router.push(`/export?id=${job.id}`);
                                                        } else {
                                                            store.loadPastProject(job.id, job.prompt, 'idle');
                                                            router.push(`/builder?prompt=${encodeURIComponent(job.prompt)}`);
                                                            setShowHistory(false);
                                                        }
                                                    }}
                                                    className="flex-1 px-3 py-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 text-xs font-semibold hover:bg-indigo-500/20 transition-colors"
                                                >
                                                    {job.phase === 'complete' ? 'Export' : 'Resume'}
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        store.loadPastProject(job.id, job.prompt, job.status || 'complete');
                                                        router.push(`/builder?prompt=${encodeURIComponent(job.prompt)}`);
                                                        setShowHistory(false);
                                                    }}
                                                    className="flex-1 px-3 py-1.5 rounded-lg bg-white/5 text-gray-300 text-xs font-semibold hover:bg-white/10 hover:text-white transition-colors"
                                                >
                                                    Upgrade
                                                </button>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
}