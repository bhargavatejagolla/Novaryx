'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    Download, FileArchive, Globe, Server, Github,
    CheckCircle2, Copy, ExternalLink, Package
} from 'lucide-react';
import { FileExplorer } from '@/components/ui/FileExplorer';
import { exportProject } from '@/lib/api';
import { cn } from '@/lib/utils';

const deployOptions = [
    {
        id: 'zip',
        name: 'Download ZIP',
        description: 'Download complete project as ZIP archive',
        icon: FileArchive,
        action: 'download',
        color: 'text-blue-400',
    },
    {
        id: 'vercel',
        name: 'Deploy to Vercel',
        description: 'One-click deploy with Vercel',
        icon: Globe,
        action: 'deploy',
        color: 'text-white',
    },
    {
        id: 'docker',
        name: 'Docker Container',
        description: 'Get Dockerfile and docker-compose.yml',
        icon: Server,
        action: 'docker',
        color: 'text-blue-300',
    },
    {
        id: 'github',
        name: 'Push to GitHub',
        description: 'Initialize git repo and push',
        icon: Github,
        action: 'github',
        color: 'text-gray-300',
    },
];

export default function ExportPage() {
    const [selected, setSelected] = useState<string>('zip');
    const [exporting, setExporting] = useState(false);
    const [done, setDone] = useState(false);

    const handleExport = async () => {
        setExporting(true);
        try {
            const result = await exportProject('latest');
            if (result.download_url && selected === 'zip') {
                window.location.href = result.download_url;
            }
            setDone(true);
        } catch (err) {
            console.error('Export failed:', err);
        } finally {
            setExporting(false);
        }
    };

    // Sample files for preview
    const sampleFiles = [
        { path: 'src/App.tsx', size: 2048, type: 'tsx' },
        { path: 'src/main.tsx', size: 512, type: 'tsx' },
        { path: 'src/components/Navbar.tsx', size: 3600, type: 'tsx' },
        { path: 'src/styles/globals.css', size: 1400, type: 'css' },
        { path: 'package.json', size: 800, type: 'json' },
        { path: 'Dockerfile', size: 600, type: '' },
        { path: 'vercel.json', size: 300, type: 'json' },
        { path: 'README.md', size: 1200, type: 'md' },
    ];

    return (
        <div className="max-w-5xl mx-auto px-6 py-8">
            <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold">Export & Deploy</h1>
                <p className="text-gray-500 mt-2">Download or deploy your generated project</p>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Export Options */}
                <div className="space-y-3">
                    {deployOptions.map((option) => (
                        <motion.button
                            key={option.id}
                            whileHover={{ scale: 1.01 }}
                            whileTap={{ scale: 0.99 }}
                            onClick={() => setSelected(option.id)}
                            className={cn(
                                'w-full text-left p-5 rounded-2xl border transition-all duration-200 flex items-start gap-4',
                                selected === option.id
                                    ? 'border-[var(--primary)]/50 bg-[var(--primary)]/5'
                                    : 'border-white/10 bg-white/5 hover:border-white/20'
                            )}
                        >
                            <div className={cn('w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center', option.color)}>
                                <option.icon className="w-5 h-5" />
                            </div>
                            <div className="flex-1">
                                <div className="font-semibold">{option.name}</div>
                                <div className="text-sm text-gray-500">{option.description}</div>
                            </div>
                            {selected === option.id && (
                                <CheckCircle2 className="w-5 h-5 text-[var(--primary)] flex-shrink-0" />
                            )}
                        </motion.button>
                    ))}

                    {/* Export Button */}
                    <motion.button
                        onClick={handleExport}
                        disabled={exporting}
                        className={cn(
                            'w-full py-4 rounded-2xl font-semibold text-lg transition-all duration-200 flex items-center justify-center gap-3 mt-4',
                            done
                                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                : 'bg-[var(--primary)] text-white hover:shadow-[0_0_30px_rgba(99,102,241,0.4)]'
                        )}
                        whileHover={!done ? { scale: 1.02 } : {}}
                        whileTap={!done ? { scale: 0.98 } : {}}
                    >
                        {exporting ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Exporting...
                            </>
                        ) : done ? (
                            <>
                                <CheckCircle2 className="w-5 h-5" />
                                Export Complete!
                            </>
                        ) : (
                            <>
                                <Download className="w-5 h-5" />
                                {selected === 'zip' ? 'Download Project' : `Deploy via ${selected}`}
                            </>
                        )}
                    </motion.button>
                </div>

                {/* File Preview */}
                <div>
                    <h3 className="font-semibold mb-4 flex items-center gap-2">
                        <Package className="w-4 h-4 text-[var(--primary)]" />
                        Project Files
                    </h3>
                    <FileExplorer files={sampleFiles} />
                </div>
            </div>
        </div>
    );
}