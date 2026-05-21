import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type OrchestrationStatus = 'idle' | 'generating' | 'complete' | 'error';
export type ModuleStatus = 'queued' | 'generating' | 'validating' | 'repairing' | 'frozen' | 'failed';

export interface OrchestrationModule {
    id: string;
    name: string;
    status: ModuleStatus;
    trustScore: number;
}

export interface OrchestrationState {
    // Global Job State
    activeJobId: string | null;
    projectName: string;
    status: OrchestrationStatus;
    globalPhase: string;
    globalProgress: number;
    error: string | null;

    // Generated Artifacts
    files: string[];
    components: string[];
    
    // Live Tracking
    terminalLogs: {text: string, time: string}[];
    completedPhaseIndices: number[];

    // DAG / Module Telemetry
    modules: Record<string, OrchestrationModule>;

    // Actions
    startJob: (jobId: string, prompt: string) => void;
    updateGlobalProgress: (phase: string, progress: number) => void;
    updateModuleStatus: (moduleId: string, status: ModuleStatus, trustScore?: number) => void;
    registerModule: (moduleId: string, name: string) => void;
    completeJob: (files: string[], components: string[], projectName: string) => void;
    failJob: (error: string) => void;
    addTerminalLog: (log: string) => void;
    markPhaseComplete: (index: number) => void;
    loadPastProject: (jobId: string, prompt: string, status: OrchestrationStatus) => void;
    reset: () => void;
}

export const useOrchestrationStore = create<OrchestrationState>()(
    persist(
        (set) => ({
            activeJobId: null,
            projectName: '',
            status: 'idle',
            globalPhase: '',
            globalProgress: 0,
            error: null,
            files: [],
            components: [],
            modules: {},
            terminalLogs: [],
            completedPhaseIndices: [],

            startJob: (jobId, prompt) => set({
                activeJobId: jobId,
                status: 'generating',
                globalPhase: 'Intent Parsing',
                globalProgress: 5,
                error: null,
                modules: {},
                terminalLogs: [],
                completedPhaseIndices: []
            }),

            updateGlobalProgress: (phase, progress) => set((state) => ({
                globalPhase: phase,
                globalProgress: Math.max(state.globalProgress, progress)
            })),

            updateModuleStatus: (moduleId, status, trustScore) => set((state) => ({
                modules: {
                    ...state.modules,
                    [moduleId]: {
                        ...state.modules[moduleId],
                        status,
                        trustScore: trustScore !== undefined ? trustScore : state.modules[moduleId]?.trustScore || 1.0
                    }
                }
            })),

            registerModule: (moduleId, name) => set((state) => ({
                modules: {
                    ...state.modules,
                    [moduleId]: {
                        id: moduleId,
                        name,
                        status: 'queued',
                        trustScore: 1.0
                    }
                }
            })),

            completeJob: (files, components, projectName) => set({
                status: 'complete',
                globalPhase: 'System Finalization',
                globalProgress: 100,
                files,
                components,
                projectName,
                completedPhaseIndices: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            }),

            failJob: (error) => set({
                status: 'error',
                error
            }),

            addTerminalLog: (log) => set((state) => ({
                terminalLogs: [...state.terminalLogs, { text: log, time: new Date().toISOString().split('T')[1].slice(0,8) }].slice(-100) // Keep last 100 logs
            })),

            markPhaseComplete: (index) => set((state) => ({
                completedPhaseIndices: state.completedPhaseIndices.includes(index) 
                    ? state.completedPhaseIndices 
                    : [...state.completedPhaseIndices, index]
            })),

            loadPastProject: (jobId, prompt, status) => set({
                activeJobId: jobId,
                status: status,
                globalPhase: status === 'complete' ? 'System Finalization' : 'Paused',
                globalProgress: status === 'complete' ? 100 : 0,
                error: null,
                // We'll let the prompt input in the builder be handled by its own local state or they can just re-type.
                // Actually the prompt isn't stored here.
                modules: {},
                terminalLogs: [],
                completedPhaseIndices: status === 'complete' ? [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] : []
            }),

            reset: () => set({
                activeJobId: null,
                projectName: '',
                status: 'idle',
                globalPhase: '',
                globalProgress: 0,
                error: null,
                files: [],
                components: [],
                modules: {},
                terminalLogs: [],
                completedPhaseIndices: []
            })
        }),
        {
            name: 'novaryx-orchestration-storage', // saves to localStorage
        }
    )
);
