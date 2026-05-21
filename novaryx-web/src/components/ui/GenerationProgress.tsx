import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, AlertCircle, FileText, Box, ShieldCheck, Cpu, Terminal, Check, Activity, XOctagon } from 'lucide-react';
import { PHASES } from '@/lib/constants';
import { cn } from '@/lib/utils';
import { useEffect, useRef } from 'react';
import { useOrchestrationStore } from '@/store/useOrchestrationStore';

export type ModuleStatus = 'queued' | 'generating' | 'validating' | 'repairing' | 'frozen' | 'failed';

interface Module {
    id: string;
    name: string;
    status?: ModuleStatus;
    trustScore?: number;
}

interface GenerationProgressProps {
    status: 'idle' | 'generating' | 'complete' | 'error';
    phase: string;
    progress: number;
    totalPhases: number;
    files: string[];
    components: string[];
    error: string | null;
    modules?: Module[];
    terminalLogs?: {text: string, time: string}[];
    completedPhaseIndices?: number[];
    className?: string;
}

export function GenerationProgress({
    status,
    phase,
    progress,
    totalPhases,
    files,
    components,
    error,
    terminalLogs = [],
    completedPhaseIndices = [],
    className,
}: GenerationProgressProps) {
    const terminalRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (terminalRef.current) {
            terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }
    }, [terminalLogs]);

    if (status === 'idle') return null;

    const completedCount = completedPhaseIndices.length;
    const progressPercentage = Math.round((completedCount / totalPhases) * 100);

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            className={cn(
                'rounded-[2rem] border shadow-2xl backdrop-blur-3xl overflow-hidden relative',
                status === 'complete'
                    ? 'border-green-500/20 bg-[#020804]/80'
                    : status === 'error'
                        ? 'border-red-500/20 bg-[#080202]/80'
                        : 'border-white/5 bg-[#030712]/80',
                className
            )}
        >
            {/* Ambient Background Glow */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[300px] bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none" />

            {/* Premium Header */}
            <div className="px-8 py-6 border-b border-white/5 bg-white/[0.02] flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
                <div className="flex items-center gap-5">
                    <div className="relative flex items-center justify-center">
                        <svg className="w-14 h-14 transform -rotate-90">
                            <circle cx="28" cy="28" r="26" stroke="currentColor" strokeWidth="2" fill="transparent" className="text-white/10" />
                            <circle 
                                cx="28" cy="28" r="26" 
                                stroke="currentColor" 
                                strokeWidth="2" 
                                fill="transparent" 
                                strokeDasharray={163.36} 
                                strokeDashoffset={163.36 - (163.36 * progressPercentage) / 100}
                                className={cn(
                                    "transition-all duration-1000 ease-out",
                                    status === 'complete' ? "text-green-500" :
                                    status === 'error' ? "text-red-500" :
                                    "text-indigo-500"
                                )} 
                            />
                        </svg>
                        <div className="absolute flex items-center justify-center">
                            {status === 'complete' ? <CheckCircle2 className="w-5 h-5 text-green-400" /> :
                             status === 'error' ? <AlertCircle className="w-5 h-5 text-red-400" /> :
                             <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />}
                        </div>
                    </div>
                    <div>
                        <h3 className="text-xl font-medium text-white tracking-tight flex items-center gap-3">
                            {status === 'complete' ? 'System Orchestration Complete' :
                             status === 'error' ? 'Orchestration Failed' :
                             'Autonomous Orchestration Active'}
                             {status === 'generating' && (
                                 <span className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-400 text-[10px] uppercase font-bold tracking-widest">
                                     <Activity className="w-3 h-3 animate-pulse" /> Live
                                 </span>
                             )}
                        </h3>
                        <p className="text-sm text-gray-400 mt-1">
                            {status === 'complete' ? 'Project is stabilized and ready for export.' :
                             error ? error :
                             <span className="flex items-center gap-2">
                                Executing Phase: <span className="text-gray-200 font-medium">{phase}</span>
                             </span>}
                        </p>
                    </div>
                </div>

                <div className="flex gap-3">
                    {(status === 'generating' || status === 'error') && (
                        <button 
                            onClick={() => useOrchestrationStore.getState().reset()}
                            className="px-4 py-2 rounded-xl bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20 transition-colors flex items-center gap-2 text-[10px] uppercase tracking-widest font-bold"
                        >
                            <XOctagon className="w-3.5 h-3.5" /> Stop / Reset
                        </button>
                    )}
                    <div className="px-4 py-2 rounded-xl bg-black/40 border border-white/5 flex items-center gap-3">
                        <div className="text-right">
                            <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-0.5">Progress</div>
                            <div className="text-sm font-semibold text-white">{completedCount} <span className="text-gray-600">/</span> {totalPhases}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-5 relative z-10 min-h-[500px]">
                
                {/* Left Column: Premium Stepper Checklist */}
                <div className="lg:col-span-2 p-8 border-r border-white/5 bg-black/20">
                    <h4 className="text-[10px] uppercase tracking-widest font-bold text-gray-500 mb-6">Execution Graph</h4>
                    <div className="space-y-0 relative">
                        {/* Connecting Line */}
                        <div className="absolute left-[11px] top-3 bottom-8 w-[2px] bg-gradient-to-b from-indigo-500/20 to-transparent" />

                        {PHASES.map((p, idx) => {
                            const isCompleted = completedPhaseIndices.includes(idx) || status === 'complete';
                            const isCurrent = !isCompleted && phase === p && status === 'generating';
                            
                            return (
                                <div key={idx} className="relative flex items-start gap-4 pb-6 group">
                                    <div className={cn(
                                        "relative z-10 w-6 h-6 rounded-full flex items-center justify-center shrink-0 border transition-all duration-500",
                                        isCompleted ? "bg-indigo-500/20 border-indigo-500/50 text-indigo-400" :
                                        isCurrent ? "bg-indigo-500 border-indigo-400 text-white shadow-[0_0_15px_rgba(99,102,241,0.5)]" :
                                        "bg-[#0a0a0a] border-white/10 text-gray-600"
                                    )}>
                                        {isCompleted ? <Check className="w-3.5 h-3.5" /> : 
                                         isCurrent ? <div className="w-2 h-2 bg-white rounded-full animate-pulse" /> : 
                                         <span className="text-[9px] font-bold">{idx + 1}</span>}
                                    </div>
                                    <div className="pt-0.5">
                                        <span className={cn(
                                            "text-sm transition-all duration-300",
                                            isCompleted ? "text-gray-400 font-medium" :
                                            isCurrent ? "text-indigo-100 font-semibold" :
                                            "text-gray-600"
                                        )}>
                                            {p}
                                        </span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Right Column: Code Editor Terminal */}
                <div className="lg:col-span-3 p-6 flex flex-col bg-black/40">
                    <div className="flex-1 rounded-2xl border border-white/5 bg-[#050505] overflow-hidden flex flex-col shadow-2xl relative">
                        {/* Editor Header */}
                        <div className="h-10 bg-white/[0.02] border-b border-white/5 flex items-center px-4 justify-between shrink-0">
                            <div className="flex gap-2">
                                <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
                                <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                                <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
                            </div>
                            <span className="text-xs font-mono text-gray-500 flex items-center gap-2">
                                <Terminal className="w-3.5 h-3.5" />
                                novaryx-engine.exe
                            </span>
                            <div className="w-10" /> {/* Spacer for centering */}
                        </div>

                        {/* Editor Content */}
                        <div 
                            ref={terminalRef}
                            className="flex-1 p-5 overflow-y-auto font-mono text-[13px] leading-relaxed space-y-1.5 custom-scrollbar"
                            style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace" }}
                        >
                            {terminalLogs.length === 0 ? (
                                <span className="text-gray-600">Initializing inference engine...</span>
                            ) : (
                                terminalLogs.map((log, i) => {
                                    const text = typeof log === 'string' ? log : (log as any).text || '';
                                    const time = typeof log === 'string' ? '' : (log as any).time || '';
                                    
                                    // Syntax highlighting heuristics
                                    const isError = text.includes('ERROR') || text.includes('failed');
                                    const isPhase = text.includes('Phase') || text.includes('success');
                                    const isHighlight = text.includes('Generating') || text.includes('Writing');
                                    
                                    return (
                                        <div key={i} className="flex gap-4 break-all hover:bg-white/[0.02] px-2 py-0.5 rounded transition-colors">
                                            {time && <span className="text-gray-600 select-none shrink-0">{time}</span>}
                                            <span className={cn(
                                                isError ? 'text-[#ff5f56]' :
                                                isPhase ? 'text-[#27c93f]' :
                                                isHighlight ? 'text-indigo-300' :
                                                'text-gray-400'
                                            )}>{text}</span>
                                        </div>
                                    );
                                })
                            )}
                            {status === 'generating' && (
                                <div className="flex gap-4 px-2 py-0.5">
                                    <span className="text-gray-600">{new Date().toISOString().split('T')[1].slice(0,8)}</span>
                                    <span className="w-2 h-4 bg-indigo-500 animate-pulse mt-1" />
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Stats Footer when Complete */}
                    <AnimatePresence>
                        {status === 'complete' && (
                            <motion.div
                                initial={{ opacity: 0, y: 10, height: 0 }}
                                animate={{ opacity: 1, y: 0, height: 'auto' }}
                                className="grid grid-cols-2 gap-4 mt-6"
                            >
                                <div className="flex items-center gap-4 p-4 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-indigo-500/30 transition-colors">
                                    <div className="w-12 h-12 rounded-full bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
                                        <FileText className="w-5 h-5 text-indigo-400" />
                                    </div>
                                    <div>
                                        <div className="text-2xl font-semibold text-white">{files.length}</div>
                                        <div className="text-[10px] uppercase text-gray-500 font-bold tracking-widest">Files Generated</div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4 p-4 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-purple-500/30 transition-colors">
                                    <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center border border-purple-500/20">
                                        <Box className="w-5 h-5 text-purple-400" />
                                    </div>
                                    <div>
                                        <div className="text-2xl font-semibold text-white">{components.length}</div>
                                        <div className="text-[10px] uppercase text-gray-500 font-bold tracking-widest">Components</div>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </motion.div>
    );
}
