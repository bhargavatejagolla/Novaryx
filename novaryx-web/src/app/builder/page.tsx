'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Wand2, Eye, Code, Download, Settings2, Palette, Layers, Cpu, FolderOpen, RefreshCw } from 'lucide-react';
import { PromptInput } from '@/components/ui/PromptInput';
import { GenerationProgress } from '@/components/ui/GenerationProgress';
import { ThemeCustomizer } from '@/components/ui/ThemeCustomizer';
import { FileExplorer } from '@/components/ui/FileExplorer';
import { LivePreview } from '@/components/ui/LivePreview';
import { useOrchestratorStream } from '@/hooks/useOrchestratorStream';
import { useOrchestrationStore } from '@/store/useOrchestrationStore';
import { useTheme } from '@/hooks/useTheme';
import { BrainCircuit, UploadCloud, ServerCrash } from 'lucide-react';

type BuilderTab = 'generate' | 'theme' | 'files' | 'preview' | 'learn';

export default function BuilderPage() {
    const searchParams = useSearchParams();
    const initialPrompt = searchParams.get('prompt') || '';
    
    const orchestratorStream = useOrchestratorStream();
    const store = useOrchestrationStore();
    const { theme, setTheme, toggleMode } = useTheme();
    const [activeTab, setActiveTab] = useState<BuilderTab>('generate');
    const [previewStatus, setPreviewStatus] = useState<'idle' | 'starting' | 'running'>('idle');
    const [previewUrl, setPreviewUrl] = useState('http://localhost:3001');

    const [mode, setMode] = useState<'new' | 'upgrade' | 'custom'>('new');
    const [projects, setProjects] = useState<any[]>([]);
    const [selectedProject, setSelectedProject] = useState<string>('');
    const [customFolderPath, setCustomFolderPath] = useState<string>('');
    const [isProjectsLoading, setIsProjectsLoading] = useState<boolean>(false);

    const fetchProjects = async () => {
        setIsProjectsLoading(true);
        try {
            const res = await fetch('/api/projects');
            const data = await res.json();
            if (data.success && data.projects) {
                setProjects(data.projects);
                if (data.projects.length > 0 && !selectedProject) {
                    setSelectedProject(data.projects[0].id);
                }
            }
        } catch (e) {
            console.error('Failed to load projects:', e);
        } finally {
            setIsProjectsLoading(false);
        }
    };

    useEffect(() => {
        fetchProjects();
    }, []);

    const handleGenerate = async (prompt: string) => {
        const options: { projectId?: string; customPath?: string } = {};
        if (mode === 'upgrade') {
            if (!selectedProject) {
                alert('Please select an existing project to upgrade.');
                return;
            }
            options.projectId = selectedProject;
        } else if (mode === 'custom') {
            if (!customFolderPath.trim()) {
                alert('Please enter a valid absolute path to the project.');
                return;
            }
            options.customPath = customFolderPath.trim();
        }
        await orchestratorStream.generate(prompt, theme, options);
    };

    const handleStartPreview = async () => {
        setPreviewStatus('starting');
        try {
            const res = await fetch('/api/projects/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'start' })
            });
            const data = await res.json();
            if (data.success) {
                // Wait 15 seconds for npm install + dev server boot before showing iframe
                setTimeout(() => {
                    setPreviewStatus('running');
                    setPreviewUrl(data.url);
                }, 15000);
            } else {
                setPreviewStatus('idle');
                alert(data.error || 'Failed to start preview server.');
            }
        } catch (err) {
            setPreviewStatus('idle');
            alert('Failed to connect to preview API.');
        }
    };

    const tabs: { id: BuilderTab; label: string; icon: any }[] = [
        { id: 'generate', label: 'Generate', icon: Wand2 },
        { id: 'theme', label: 'Theme', icon: Palette },
        { id: 'files', label: 'Files', icon: Layers },
        { id: 'preview', label: 'Preview', icon: Eye },
        { id: 'learn', label: 'Teach', icon: BrainCircuit },
    ];

    return (
        <div className="max-w-7xl mx-auto px-6 py-8">
            <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold">Visual Builder</h1>
                <p className="text-gray-500 mt-2">Design, generate, and preview your application</p>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Panel */}
                <div className="lg:col-span-1 space-y-4">
                    {/* Tabs */}
                    <div className="flex gap-1 p-1 rounded-xl bg-white/5">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                                    ? 'bg-[var(--primary)] text-white'
                                    : 'text-gray-500 hover:text-white'
                                    }`}
                            >
                                <tab.icon className="w-4 h-4" />
                                {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Tab Content */}
                    <div className="glass rounded-2xl p-5">
                        {activeTab === 'generate' && (
                            <div className="space-y-4">
                                <h3 className="font-semibold text-white mb-2">Build & Update Engine</h3>
                                
                                {/* Mode Selection Tabs */}
                                <div className="flex gap-1 p-1 rounded-xl bg-white/5 border border-white/10">
                                    <button
                                        onClick={() => setMode('new')}
                                        className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
                                            mode === 'new'
                                                ? 'bg-indigo-600 text-white shadow-md'
                                                : 'text-gray-400 hover:text-white hover:bg-white/5'
                                        }`}
                                    >
                                        <Wand2 className="w-3.5 h-3.5" />
                                        New App
                                    </button>
                                    <button
                                        onClick={() => setMode('upgrade')}
                                        className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
                                            mode === 'upgrade'
                                                ? 'bg-indigo-600 text-white shadow-md'
                                                : 'text-gray-400 hover:text-white hover:bg-white/5'
                                        }`}
                                    >
                                        <RefreshCw className="w-3.5 h-3.5" />
                                        Upgrade Existing
                                    </button>
                                    <button
                                        onClick={() => setMode('custom')}
                                        className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
                                            mode === 'custom'
                                                ? 'bg-indigo-600 text-white shadow-md'
                                                : 'text-gray-400 hover:text-white hover:bg-white/5'
                                        }`}
                                    >
                                        <FolderOpen className="w-3.5 h-3.5" />
                                        Custom Path
                                    </button>
                                </div>

                                {/* Dynamic Helper / Mode Inputs */}
                                <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-3">
                                    {mode === 'new' && (
                                        <p className="text-xs text-gray-400">
                                            Compose a brand-new application. Our autonomous agent pipeline will handle standard architecture decomposition, code generation, and multi-round bug repair from scratch.
                                        </p>
                                    )}

                                    {mode === 'upgrade' && (
                                        <div className="space-y-2">
                                            <p className="text-xs text-gray-400">
                                                Select a project from your deployment checklist. Changes are applied surgically to files to resolve errors or add features without wiping out existing custom updates.
                                            </p>
                                            <div className="flex gap-2">
                                                <div className="relative flex-1">
                                                    <select
                                                        value={selectedProject}
                                                        onChange={(e) => setSelectedProject(e.target.value)}
                                                        disabled={isProjectsLoading || projects.length === 0}
                                                        className="w-full bg-surface/50 border border-white/10 hover:border-white/20 rounded-xl px-3 py-2 text-sm text-white font-medium outline-none focus:border-indigo-500 transition-colors appearance-none cursor-pointer"
                                                    >
                                                        {projects.length === 0 ? (
                                                            <option value="" className="bg-surface text-gray-400">No generated projects found</option>
                                                        ) : (
                                                            projects.map((proj) => (
                                                                <option key={proj.id} value={proj.id} className="bg-surface text-white">
                                                                    {proj.name} ({proj.id.substring(0, 8)})
                                                                </option>
                                                            ))
                                                        )}
                                                    </select>
                                                    <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                                                        ▼
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={fetchProjects}
                                                    disabled={isProjectsLoading}
                                                    title="Refresh Projects"
                                                    className="p-2.5 rounded-xl bg-surface/50 border border-white/10 hover:border-white/20 text-gray-400 hover:text-white transition-colors flex items-center justify-center"
                                                >
                                                    <RefreshCw className={`w-4 h-4 ${isProjectsLoading ? 'animate-spin' : ''}`} />
                                                </button>
                                            </div>
                                        </div>
                                    )}

                                    {mode === 'custom' && (
                                        <div className="space-y-2">
                                            <p className="text-xs text-gray-400">
                                                Enter the full absolute directory path of any local project. Ideal for debugging or extending components in foreign codebases.
                                            </p>
                                            <input
                                                type="text"
                                                value={customFolderPath}
                                                onChange={(e) => setCustomFolderPath(e.target.value)}
                                                placeholder="e.g., C:\Users\YourName\projects\my-app"
                                                className="w-full bg-surface/50 border border-white/10 hover:border-white/20 rounded-xl px-3 py-2 text-sm text-white placeholder-gray-500 outline-none focus:border-indigo-500 transition-colors"
                                            />
                                        </div>
                                    )}
                                </div>

                                <PromptInput 
                                    onSubmit={handleGenerate} 
                                    loading={store.status === 'generating'} 
                                    initialPrompt={initialPrompt}
                                    buttonText={mode === 'new' ? 'Generate' : mode === 'upgrade' ? 'Apply Upgrade' : 'Apply to Folder'}
                                    placeholder={
                                        mode === 'new' 
                                            ? 'Describe what you want to build...' 
                                            : mode === 'upgrade' 
                                                ? 'Specify errors or feature requests to apply to the selected project...' 
                                                : 'Specify fixes or features to apply to this custom directory...'
                                    }
                                />

                                {store.status !== 'idle' && (
                                    <div className="mt-4 p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm">
                                        Generation in progress. Check the main console.
                                    </div>
                                )}
                            </div>
                        )}

                        {activeTab === 'theme' && (
                            <div>
                                <h3 className="font-semibold mb-4">Theme Customizer</h3>
                                <ThemeCustomizer
                                    theme={theme}
                                    onThemeChange={setTheme}
                                    onToggleMode={toggleMode}
                                />
                            </div>
                        )}

                        {activeTab === 'files' && store.files.length > 0 && (
                            <div>
                                <h3 className="font-semibold mb-4">Project Files</h3>
                                <FileExplorer files={store.files.map((f: string) => ({ path: f, size: 0, type: f.split('.').pop() || 'unknown' }))} />
                            </div>
                        )}

                        {activeTab === 'files' && store.files.length === 0 && (
                            <div className="text-center py-8 text-gray-500">
                                <Layers className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                <p>Generate a project to see files</p>
                            </div>
                        )}

                        {activeTab === 'preview' && (
                            <div className="text-center py-8 text-gray-500">
                                <Eye className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                <p>Preview available in the main panel</p>
                            </div>
                        )}

                        {activeTab === 'learn' && (
                            <div>
                                <h3 className="font-semibold mb-4">Teach Novaryx</h3>
                                <p className="text-sm text-gray-400 mb-6">
                                    Upload custom React components (.tsx) or CSS files to index them into NOVARYX's ChromaDB RAG. The engine will analyze them using Groq and use them in future generations.
                                </p>

                                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-[var(--primary)]/30 border-dashed rounded-xl cursor-pointer bg-white/5 hover:bg-white/10 transition-colors">
                                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                        <UploadCloud className="w-8 h-8 mb-2 text-gray-400" />
                                        <p className="text-sm text-gray-400"><span className="font-semibold text-white">Click to upload</span> or drag and drop</p>
                                        <p className="text-xs text-gray-500">.tsx, .css files</p>
                                    </div>
                                    <input
                                        type="file"
                                        className="hidden"
                                        accept=".tsx,.css"
                                        onChange={async (e) => {
                                            const file = e.target.files?.[0];
                                            if (!file) return;

                                            const reader = new FileReader();
                                            reader.onload = async (event) => {
                                                const content = event.target?.result as string;
                                                const name = file.name.replace(/\.[^/.]+$/, "");

                                                try {
                                                    const res = await fetch('/api/learn', {
                                                        method: 'POST',
                                                        headers: { 'Content-Type': 'application/json' },
                                                        body: JSON.stringify({ name, code: content })
                                                    });

                                                    const data = await res.json();
                                                    if (data.success) {
                                                        alert(`Successfully taught Novaryx: ${name}`);
                                                    } else {
                                                        alert(`Failed: ${data.error}`);
                                                    }
                                                } catch (err) {
                                                    alert('Upload failed');
                                                }
                                            };
                                            reader.readAsText(file);
                                        }}
                                    />
                                </label>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Panel — Preview */}
                <div className="lg:col-span-2">
                    {store.status === 'complete' ? (
                        previewStatus === 'running' ? (
                            <LivePreview projectUrl={previewUrl} />
                        ) : previewStatus === 'starting' ? (
                            <div className="glass rounded-2xl p-12 text-center border-indigo-500/20 bg-indigo-500/5">
                                <div className="w-16 h-16 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto mb-6" />
                                <h3 className="text-xl font-semibold text-white mb-2">Bootstrapping Dev Server...</h3>
                                <p className="text-gray-400 max-w-sm mx-auto">
                                    Installing required Node packages and launching the local server on port 3001. This will take about 15 seconds.
                                </p>
                            </div>
                        ) : (
                            <div className="glass rounded-2xl p-12 text-center border-indigo-500/20">
                                <Wand2 className="w-16 h-16 text-indigo-400 mx-auto mb-6" />
                                <h3 className="text-xl font-semibold text-white mb-2">Project Generated Successfully!</h3>
                                <p className="text-gray-400 max-w-md mx-auto mb-8">
                                    Your full SaaS platform is compiled. Click below to start the local proxy live server and preview the interface.
                                </p>
                                <button
                                    onClick={handleStartPreview}
                                    className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-colors shadow-lg shadow-indigo-500/25"
                                >
                                    Start Live Preview Server
                                </button>
                            </div>
                        )
                    ) : store.status === 'generating' ? (
                        <div className="h-full">
                            <GenerationProgress
                                {...store}
                                modules={Object.values(store.modules)}
                                phase={store.globalPhase}
                                progress={store.globalProgress}
                                totalPhases={12}
                                className="h-full border-none shadow-none bg-transparent"
                            />
                        </div>
                    ) : (
                        <div className="glass rounded-2xl p-12 text-center h-full flex flex-col items-center justify-center border-white/5">
                            <Wand2 className="w-16 h-16 text-gray-700 mb-6" />
                            <h3 className="text-2xl font-bold text-white mb-2">Ready to Orchesrate</h3>
                            <p className="text-gray-500 max-w-md leading-relaxed">
                                Enter your development requirements on the left.<br />
                                Our autonomous engine will handle decomposition, generation, and repair.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}