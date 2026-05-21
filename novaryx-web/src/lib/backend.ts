// NOVARYX Backend Bridge (Upgraded)
// Connects Next.js frontend to Python backend (novaryx_e2e.py)
// Supports: streaming SSE, structured JSON result, status checks
// Provider priority: auto-selected by Python (Groq → Ollama → Gemini)

import { spawn, execSync, spawnSync } from 'child_process';
import path from 'path';
import fs from 'fs';
import os from 'os';

const BACKEND_ROOT = path.join(process.cwd(), '..');
const VENV_PYTHON = process.platform === 'win32'
    ? path.join(BACKEND_ROOT, 'venv', 'Scripts', 'python.exe')
    : path.join(BACKEND_ROOT, 'venv', 'bin', 'python3');

function getPythonExe(): string {
    if (fs.existsSync(VENV_PYTHON)) return VENV_PYTHON;
    return process.platform === 'win32' ? 'python' : 'python3';
}

export interface GenerationResult {
    success: boolean;
    project_name: string;
    files: string[];
    components: string[];
    componentCount?: number;
    pages?: number;
    bugs_fixed?: number;
    export_path?: string;
    errors: string[];
}

export interface StreamEvent {
    type: 'progress' | 'result' | 'error';
    message?: string;
    result?: GenerationResult;
}

export class BackendBridge {
    private static wsProcess: any = null;

    // ──────────────────────────────────────────────────────────────────
    // Backend lifecycle
    // ──────────────────────────────────────────────────────────────────

    static startBackend(): boolean {
        try {
            this.wsProcess = spawn(getPythonExe(), [
                '-c',
                'from system.realtime.websocket_server import WebSocketServer; server = WebSocketServer(); server.start(); import time; time.sleep(999999)',
            ], { cwd: BACKEND_ROOT, stdio: 'pipe' });
            console.log('✅ WebSocket server started on ws://localhost:9001');
            return true;
        } catch (error) {
            console.error('❌ Failed to start backend:', error);
            return false;
        }
    }

    static stopBackend() {
        if (this.wsProcess) { this.wsProcess.kill(); this.wsProcess = null; }
    }

    static isBackendRunning(): boolean {
        return this.wsProcess !== null && !this.wsProcess.killed;
    }

    // ──────────────────────────────────────────────────────────────────
    // Streaming generation (spawn-based, non-blocking)
    // Calls novaryx_e2e.py with real LLM — no --no-llm
    // ──────────────────────────────────────────────────────────────────

    static generateStream(
        prompt: string,
        options: { projectId?: string; customPath?: string } | undefined,
        onProgress: (msg: string) => void,
        onResult: (result: GenerationResult) => void,
        onError: (err: string) => void,
        abortSignal?: AbortSignal
    ): void {
        const pythonExe = getPythonExe();
        let pythonScript = path.join(BACKEND_ROOT, 'novaryx_e2e.py');
        let args: string[] = ['-u'];
        
        const isUpdate = options?.projectId || options?.customPath;
        
        if (isUpdate) {
            pythonScript = path.join(BACKEND_ROOT, 'novaryx_update.py');
            let targetPath = '';
            if (options?.customPath) {
                targetPath = options.customPath;
            } else if (options?.projectId) {
                const homedir = os.homedir();
                const exportsDir = path.join(homedir, 'novaryx', 'exports');
                targetPath = path.join(exportsDir, options.projectId);
            }
            
            console.log(`🔄 NOVARYX streaming update on: ${targetPath}`);
            args.push(pythonScript, prompt, '--project-dir', targetPath);
        } else {
            console.log(`🚀 NOVARYX streaming generate: "${prompt.slice(0, 60)}…"`);
            args.push(pythonScript, prompt);
        }

        const proc = spawn(pythonExe, args, {
            cwd: BACKEND_ROOT,
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
            stdio: ['ignore', 'pipe', 'pipe'],
        });

        let buffer = '';
        let resultFound = false;

        proc.stdout.on('data', (chunk: Buffer) => {
            buffer += chunk.toString('utf-8');
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('STREAM_TOKEN:')) {
                    onProgress(line.replace('STREAM_TOKEN:', '').trim());
                } else if (line.startsWith('GENERATION_RESULT:')) {
                    try {
                        const json = line.replace('GENERATION_RESULT:', '').trim();
                        const parsed = JSON.parse(json) as GenerationResult;
                        resultFound = true;
                        onResult(parsed);
                    } catch {
                        // malformed JSON — ignore
                    }
                }
            }
        });

        proc.stderr.on('data', (chunk: Buffer) => {
            const msg = chunk.toString('utf-8');
            // Only surface actual errors (not INFO/WARNING logs)
            if (msg.includes('ERROR') || msg.includes('Traceback')) {
                console.error('Backend error:', msg.slice(-500));
            }
        });

        proc.on('close', (code: number) => {
            if (!resultFound) {
                onError(`Process exited with code ${code} — no result produced`);
            }
        });

        proc.on('error', (err: Error) => {
            onError(err.message);
        });

        // 20-minute timeout watchdog (pattern-only repair is fast; large projects still need time)
        const timeout = setTimeout(() => {
            proc.kill('SIGTERM');
            if (!resultFound) {
                onError('Generation timed out after 20 minutes');
            }
        }, 20 * 60 * 1000);

        proc.on('close', () => clearTimeout(timeout));
        
        // Listen for client aborts (e.g. browser tab closed)
        if (abortSignal) {
            abortSignal.addEventListener('abort', () => {
                console.log('🛑 Client disconnected. Killing Python generation process...');
                proc.kill('SIGTERM');
                clearTimeout(timeout);
            });
        }
    }

    // ──────────────────────────────────────────────────────────────────
    // Synchronous generation (for API routes that need a return value)
    // ──────────────────────────────────────────────────────────────────

    static generate(prompt: string, _theme?: any): GenerationResult {
        const pythonExe = getPythonExe();
        const pythonScript = path.join(BACKEND_ROOT, 'novaryx_e2e.py');
        const escapedPrompt = prompt.replace(/"/g, '\\"').replace(/\n/g, ' ');
        const command = `"${pythonExe}" "${pythonScript}" "${escapedPrompt}"`;

        console.log(`🚀 NOVARYX sync generate: "${prompt.slice(0, 60)}…"`);

        try {
            const output = execSync(command, {
                cwd: BACKEND_ROOT,
                timeout: 1_200_000,  // 20 minutes
                encoding: 'utf-8',
                maxBuffer: 20 * 1024 * 1024,
                env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
            });

            return this.parseOutput(output);
        } catch (error: any) {
            const stderr = error.stderr?.slice(-800) || error.message || '';
            console.error('Generation error:', stderr);
            return {
                success: false,
                project_name: '',
                files: [],
                components: [],
                errors: [stderr || 'Generation failed'],
            };
        }
    }

    // ──────────────────────────────────────────────────────────────────
    // Output parsing
    // ──────────────────────────────────────────────────────────────────

    static parseOutput(output: string): GenerationResult {
        // Primary: structured JSON line
        const jsonMatch = output.match(/GENERATION_RESULT:\s*(\{[\s\S]+?\})\s*$/m);
        if (jsonMatch) {
            try {
                return JSON.parse(jsonMatch[1]) as GenerationResult;
            } catch { /* fall through */ }
        }

        // Fallback: heuristic parsing
        const result: GenerationResult = {
            success: output.includes('GENERATION COMPLETE') || output.includes('🏆'),
            project_name: '',
            files: [],
            components: [],
            errors: [],
        };

        const nameMatch = output.match(/Project:\s*(.+)/);
        if (nameMatch) result.project_name = nameMatch[1].trim();

        const fileRegex = /\[(?:LLM|template|OK)\]\s+(.+)/g;
        let m;
        while ((m = fileRegex.exec(output)) !== null) {
            result.files.push(m[1].trim());
        }

        const errorRegex = /ERROR\s*\|(.+)/g;
        while ((m = errorRegex.exec(output)) !== null) {
            result.errors.push(m[1].trim());
        }

        return result;
    }

    // ──────────────────────────────────────────────────────────────────
    // System status
    // ──────────────────────────────────────────────────────────────────

    static getStatus(): any {
        return {
            backend_running:  this.isBackendRunning(),
            python:           this.getPythonVersion(),
            provider:         this.getActiveProvider(),
            models:           this.getOllamaModels(),
            groq_configured:  !!process.env.GROQ_API_KEY,
            memory:           this.getMemoryStats(),
        };
    }

    private static getPythonVersion(): string {
        try {
            return execSync(`"${getPythonExe()}" --version`, {
                encoding: 'utf-8', timeout: 5000,
                env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
            }).trim();
        } catch { return 'Not found'; }
    }

    private static getActiveProvider(): string {
        try {
            const backendPath = BACKEND_ROOT.replace(/\\/g, '/');
            const out = execSync(
                `"${getPythonExe()}" -c "import sys; sys.path.insert(0,'${backendPath}'); from system.inference.provider_factory import get_current_provider_info; import json; print(json.dumps(get_current_provider_info()))"`,
                { cwd: BACKEND_ROOT, encoding: 'utf-8', timeout: 15_000,
                  env: { ...process.env, PYTHONIOENCODING: 'utf-8' } }
            );
            const info = JSON.parse(out.trim().split('\n').pop()!);
            return info.name || 'unknown';
        } catch { return 'unknown'; }
    }

    private static getOllamaModels(): string[] {
        try {
            const output = execSync('ollama list', { encoding: 'utf-8', timeout: 5000 });
            return output.split('\n').slice(1).filter(Boolean)
                .map((l) => l.split(/\s+/)[0]).filter(Boolean);
        } catch { return []; }
    }

    private static getMemoryStats(): any {
        try {
            const memoryFile = path.join(
                process.env.HOME || process.env.USERPROFILE || '',
                'novaryx', 'memory', 'memory_index.json'
            );
            if (fs.existsSync(memoryFile)) {
                const data = JSON.parse(fs.readFileSync(memoryFile, 'utf-8'));
                return { projects: data.total_memories || 0 };
            }
        } catch { }
        return { projects: 0 };
    }

    static checkHealth(): { success: boolean; data?: any; error?: string } {
        try {
            const pythonExe = getPythonExe();
            const pythonScript = path.join(BACKEND_ROOT, 'system', 'health.py');
            const command = `"${pythonExe}" "${pythonScript}" --json`;
            const output = execSync(command, {
                cwd: BACKEND_ROOT,
                timeout: 10000,
                encoding: 'utf-8',
            });
            const data = JSON.parse(output.trim());
            return { success: data.overall !== 'error', data };
        } catch (err: any) {
            return { success: false, error: err.message };
        }
    }

    /**
     * Lists all generated projects by reading the checkpoints.
     */
    static listJobs(): any[] {
        try {
            const jobs: any[] = [];
            const homedir = os.homedir();
            
            // 1. Read from StateManager home folder directory
            const homeStateDir = path.join(homedir, 'novaryx', 'state');
            if (fs.existsSync(homeStateDir)) {
                const files = fs.readdirSync(homeStateDir);
                for (const file of files) {
                    if (file.endsWith('.json') && file !== 'active_state.json') {
                        try {
                            const data = JSON.parse(fs.readFileSync(path.join(homeStateDir, file), 'utf-8'));
                            const meta = data.meta || {};
                            jobs.push({
                                id: meta.generation_id || file.replace('.json', ''),
                                name: meta.project_name || 'NOVARYX Project',
                                timestamp: meta.last_saved || meta.created_at || new Date().toISOString(),
                                phase: meta.current_phase || 'completed',
                                status: meta.completed_phases === meta.total_phases ? 'completed' : 'in_progress',
                                prompt: meta.prompt || 'Project',
                                type: 'Web App',
                                components: data.data?.components ? Object.keys(data.data.components) : [],
                                files: meta.completed_phases || 12,
                                success: meta.completed_phases === meta.total_phases,
                                quality: 100,
                                created: meta.created_at || new Date().toISOString(),
                                primaryColor: '#7c3aed'
                            });
                        } catch (e) {
                            // ignore malformed
                        }
                    }
                }
            }

            // 2. Read from legacy/workspace projects directory (fallback/double safety)
            const projectsDir = path.join(BACKEND_ROOT, 'projects');
            if (fs.existsSync(projectsDir)) {
                const dirs = fs.readdirSync(projectsDir);
                for (const dir of dirs) {
                    const checkpointPath = path.join(projectsDir, dir, 'checkpoint.json');
                    if (fs.existsSync(checkpointPath)) {
                        try {
                            const data = JSON.parse(fs.readFileSync(checkpointPath, 'utf-8'));
                            // Prevent duplicates
                            if (!jobs.some(j => j.id === dir)) {
                                jobs.push({
                                    id: dir,
                                    name: data.project_name || 'NOVARYX Project',
                                    timestamp: data.timestamp || data.updated_at || new Date().toISOString(),
                                    phase: data.phase || 'completed',
                                    status: data.metadata?.status || 'completed',
                                    prompt: data.prompt || 'Project',
                                    type: 'Web App',
                                    components: [],
                                    files: 12,
                                    success: true,
                                    quality: 100,
                                    created: data.created_at || data.timestamp || new Date().toISOString(),
                                    primaryColor: '#7c3aed'
                                });
                            }
                        } catch (e) {
                            // ignore
                        }
                    }
                }
            }
            
            return jobs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        } catch (err) {
            console.error('Failed to list jobs:', err);
            return [];
        }
    }

    /**
     * Ingests a new component into the NOVARYX memory for continuous learning.
     * @param name Component name
     * @param code React/TSX code
     */
    static ingestComponent(name: string, code: string): { success: boolean; result?: any; error?: string } {
        try {
            const tempFile = path.join(os.tmpdir(), `novaryx_ingest_${Date.now()}.tsx`);
            fs.writeFileSync(tempFile, code, 'utf-8');

            const script = `
import sys
import json
from pathlib import Path
sys.path.insert(0, r'${BACKEND_ROOT}')
from system.memory.ingestion_pipeline import IngestionPipeline
pipeline = IngestionPipeline()
res = pipeline.ingest_component('${name}', open(r'${tempFile.replace(/\\/g, '\\\\')}', 'r', encoding='utf-8').read())
print(json.dumps(res) if res else json.dumps({'error': 'Failed to ingest'}))
`;
            
            const result = spawnSync(getPythonExe(), ['-X', 'utf8', '-c', script], {
                cwd: BACKEND_ROOT,
                encoding: 'utf-8',
                maxBuffer: 1024 * 1024 * 10,
            });

            fs.unlinkSync(tempFile);

            if (result.error) throw result.error;

            const lines = result.stdout.split('\\n');
            const jsonLine = lines.find((l: string) => l.trim().startsWith('{'));
            if (jsonLine) {
                const parsed = JSON.parse(jsonLine);
                if (parsed.error) return { success: false, error: parsed.error };
                return { success: true, result: parsed };
            }

            return { success: false, error: 'Invalid response from ingestion pipeline: ' + result.stderr };
        } catch (error: any) {
            console.error('Ingestion failed:', error);
            return { success: false, error: error.message };
        }
    }
}
