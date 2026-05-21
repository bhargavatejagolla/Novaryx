import { useCallback } from 'react';
import { useOrchestrationStore } from '@/store/useOrchestrationStore';
import { PHASES } from '@/lib/constants';

export function useOrchestratorStream() {
    const store = useOrchestrationStore();

    const generate = useCallback(async (prompt: string, theme?: any, options?: { projectId?: string; customPath?: string }) => {
        const jobId = options?.projectId || store.activeJobId || Math.random().toString(36).substring(7);
        store.startJob(jobId, prompt);

        try {
            const response = await fetch('/api/generate/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    prompt, 
                    theme,
                    projectId: options?.projectId,
                    customPath: options?.customPath
                }),
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

                                if (phaseIdx >= 0) {
                                    const progressVal = ((phaseIdx + 1) / 12) * 100;
                                    store.updateGlobalProgress(phaseName, progressVal);
                                    
                                    // Mark all previous phases as complete
                                    if (phaseIdx > 0) {
                                        for(let i=0; i<phaseIdx; i++) {
                                            store.markPhaseComplete(i);
                                        }
                                    }
                                } else {
                                    // Make progress creep up slowly
                                    useOrchestrationStore.setState(s => ({
                                        globalPhase: phaseName,
                                        globalProgress: Math.min(95, s.globalProgress + 2)
                                    }));
                                }
                                
                                // Push raw log to terminal UI
                                store.addTerminalLog(msg);
                                
                            } else if (parsed.type === 'architecture') {
                                // Dynamic DAG Module events
                                parsed.modules?.forEach((m: any) => {
                                    store.registerModule(m.id, m.name);
                                });
                            } else if (parsed.type === 'telemetry') {
                                // New standard for orchestrator events
                                // E.g. { type: 'telemetry', module: 'dashboard', status: 'validating', trust: 0.94 }
                                if (parsed.module && parsed.status) {
                                    store.updateModuleStatus(parsed.module, parsed.status, parsed.trust);
                                }
                            } else if (parsed.type === 'result') {
                                const result = parsed.result;
                                store.completeJob(
                                    result.files || [],
                                    result.components || [],
                                    result.project_name || 'My Project'
                                );
                                return result;
                            } else if (parsed.type === 'error') {
                                store.failJob(parsed.message || 'Stream error');
                                return;
                            }
                        } catch (e: any) {
                            console.error('Error parsing stream chunk:', e);
                        }
                    }
                }
            }
        } catch (err: any) {
            store.failJob(err.message || 'Generation failed');
            throw err;
        }
    }, [store]);

    return { generate };
}
