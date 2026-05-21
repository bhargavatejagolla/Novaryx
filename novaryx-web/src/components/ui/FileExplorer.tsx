'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Folder, ChevronRight, Code, FileJson, FileType, Image } from 'lucide-react';
import { cn, formatBytes } from '@/lib/utils';

interface FileNode {
    name: string;
    path: string;
    type: 'file' | 'folder';
    size?: number;
    children?: FileNode[];
}

interface FileExplorerProps {
    files: { path: string; size: number; type: string }[];
    className?: string;
}

function getFileIcon(fileName: string) {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
        case 'tsx':
        case 'ts':
            return <FileType className="w-4 h-4 text-blue-400" />;
        case 'css':
            return <Code className="w-4 h-4 text-purple-400" />;
        case 'json':
            return <FileJson className="w-4 h-4 text-yellow-400" />;
        case 'jsx':
        case 'js':
            return <FileType className="w-4 h-4 text-yellow-300" />;
        default:
            return <FileText className="w-4 h-4 text-gray-400" />;
    }
}

function FileRow({ name, size, depth = 0 }: { name: string; size?: number; depth?: number }) {
    return (
        <div
            className={cn(
                'flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-white/5 rounded-lg transition-colors cursor-pointer group'
            )}
            style={{ paddingLeft: `${12 + depth * 16}px` }}
        >
            {getFileIcon(name)}
            <span className="text-gray-300 flex-1 truncate">{name}</span>
            {size !== undefined && (
                <span className="text-xs text-gray-600 group-hover:text-gray-400">{formatBytes(size)}</span>
            )}
        </div>
    );
}

export function FileExplorer({ files, className }: FileExplorerProps) {
    const [expanded, setExpanded] = useState<Set<string>>(new Set(['src', 'src/components', 'src/pages']));

    // Build file tree
    const tree: Record<string, any> = {};
    for (const file of files) {
        const parts = file.path.split('/');
        let current = tree;
        for (let i = 0; i < parts.length; i++) {
            const part = parts[i];
            if (i === parts.length - 1) {
                current[part] = { type: 'file', size: file.size };
            } else {
                if (!current[part]) current[part] = { type: 'folder', children: {} };
                current = current[part].children;
            }
        }
    }

    function renderTree(node: Record<string, any>, path: string = '', depth: number = 0) {
        return Object.entries(node).map(([name, info]) => {
            const fullPath = path ? `${path}/${name}` : name;
            const isFolder = info.type === 'folder' || info.children;
            const isExpanded = expanded.has(fullPath);

            if (isFolder) {
                return (
                    <div key={fullPath}>
                        <button
                            onClick={() => {
                                const next = new Set(expanded);
                                if (isExpanded) next.delete(fullPath);
                                else next.add(fullPath);
                                setExpanded(next);
                            }}
                            className="flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-white/5 rounded-lg transition-colors w-full text-left"
                            style={{ paddingLeft: `${12 + depth * 16}px` }}
                        >
                            <motion.div
                                animate={{ rotate: isExpanded ? 90 : 0 }}
                                transition={{ duration: 0.2 }}
                            >
                                <ChevronRight className="w-3.5 h-3.5 text-gray-500" />
                            </motion.div>
                            <Folder className="w-4 h-4 text-[var(--primary)]" />
                            <span className="text-gray-300">{name}</span>
                        </button>
                        <AnimatePresence>
                            {isExpanded && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    {renderTree(info.children || {}, fullPath, depth + 1)}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                );
            }

            return <FileRow key={fullPath} name={name} size={info.size} depth={depth} />;
        });
    }

    return (
        <div className={cn('rounded-2xl border border-white/10 bg-surface/30 p-3', className)}>
            <div className="text-xs text-gray-500 uppercase tracking-wider px-3 py-2 mb-1">
                Project Files ({files.length})
            </div>
            <div className="space-y-0.5 max-h-96 overflow-y-auto">
                {renderTree(tree)}
            </div>
        </div>
    );
}