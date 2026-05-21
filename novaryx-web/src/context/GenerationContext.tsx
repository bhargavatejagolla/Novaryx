'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import { PHASES } from '@/lib/constants';

interface GenerationState {
    status: 'idle' | 'generating' | 'complete' | 'error';
    phase: string;
    progress: number;
    totalPhases: number;
    files: string[];
    components: string[];
    projectName: string;
    error: string | null;
    modules: { id: string, name: string }[];
    completedModules: string[];
}

const initialState: GenerationState = {
    status: 'idle',
    phase: '',
    progress: 0,
    totalPhases: 12,
    files: [],
    components: [],
    projectName: '',
    error: null,
    modules: [],
    completedModules: [],
};

interface GenerationContextType extends GenerationState {
    generate: (prompt: string, theme?: any) => Promise<any>;
    reset: () => void;
}

const GenerationContext = createContext<GenerationContextType | undefined>(undefined);

export function GenerationProvider({ children }: { children: React.ReactNode }) {
    const [state, setState] = useState<GenerationState>(initialState);

    const generate = useCallback(async (prompt: string, theme?: any) => {
        setState({
            ...initialState,
            status: 'generating',
            phase: 'Starting...',
            progress: 5,
        });

        try {
            const response = await fetch('/api/generate/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, theme }),
            });

            if (!response.ok) {
                throw new Error('Generation failed to start');
            }

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();
            if (!reader) throw new Error('No stream readable');

            let buffer = '';
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.trim().startsWith('data: ')) {
                        try {
                            const jsonStr = line.replace('data: ', '').trim();
                            const parsed = JSON.parse(jsonStr);

                            if (parsed.type === 'progress') {
                                const msg = parsed.message || '';
                                let phaseIdx = -1;
                                let phaseName = msg;

                                // Match python phase tags to frontend PHASES
                                if (msg.includes('Phase 1:')) { phaseIdx = 0; phaseName = PHASES[0]; }
                                else if (msg.includes('Phase 6:')) { phaseIdx = 5; phaseName = PHASES[5]; }
                                else if (msg.includes('Phase 7:')) { phaseIdx = 6; phaseName = PHASES[6]; }
                                else if (msg.includes('Phase 8:')) { phaseIdx = 7; phaseName = PHASES[7]; }
                                else if (msg.includes('Phase 9:') && msg.includes('complete')) { phaseIdx = 8; phaseName = PHASES[8]; }
                                else if (msg.includes('Phase 9:')) { phaseIdx = 8; phaseName = PHASES[8]; }
                                else if (msg.includes('Phase 10:') && msg.includes('complete')) { phaseIdx = 10; phaseName = PHASES[10]; }
                                else if (msg.includes('Phase 10:')) { phaseIdx = 9; phaseName = PHASES[9]; }
                                else if (msg.includes('Phase 11:')) { phaseIdx = 10; phaseName = PHASES[10]; }

                                setState((prev) => {
                                    const progressVal = phaseIdx >= 0
                                        ? ((phaseIdx + 1) / prev.totalPhases) * 100
                                        : prev.progress + 2;

                                    return {
                                        ...prev,
                                        phase: phaseName,
                                        progress: Math.min(progressVal, 95),
                                    };
                                });
                            } else if (parsed.type === 'architecture') {
                                setState((prev) => ({
                                    ...prev,
                                    modules: parsed.modules || [],
                                    totalPhases: (parsed.modules || []).length + 4
                                }));
                            } else if (parsed.type === 'result') {
                                const result = parsed.result;
                                setState({
                                    status: 'complete',
                                    phase: 'Complete',
                                    progress: 100,
                                    totalPhases: 12,
                                    files: result.files || [],
                                    components: result.components || [],
                                    projectName: result.project_name || 'My Project',
                                    error: null,
                                    modules: [],
                                    completedModules: [],
                                });
                                return result;
                            } else if (parsed.type === 'error') {
                                const errMsg = parsed.message || 'Stream error during generation';
                                setState((prev) => ({
                                    ...prev,
                                    status: 'error',
                                    error: errMsg,
                                }));
                                return;
                            }
                        } catch (e: any) {
                            console.error('Error parsing stream chunk:', e);
                        }
                    }
                }
            }
        } catch (err: any) {
            setState((prev) => ({
                ...prev,
                status: 'error',
                error: err.message || 'Generation failed',
            }));
            throw err;
        }
    }, []);

    const reset = useCallback(() => {
        setState(initialState);
    }, []);

    return (
        <GenerationContext.Provider value={{ ...state, generate, reset }}>
            {children}
        </GenerationContext.Provider>
    );
}

export function useGenerationContext() {
    const context = useContext(GenerationContext);
    if (!context) {
        throw new Error('useGenerationContext must be used within a GenerationProvider');
    }
    return context;
}
