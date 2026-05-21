'use client';

import { motion } from 'framer-motion';
import { Code, Layers, Eye } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ComponentPreviewProps {
    name: string;
    type: string;
    description: string;
    code?: string;
    keywords?: string[];
    complexity?: string;
    className?: string;
}

export function ComponentPreview({
    name,
    type,
    description,
    code,
    keywords,
    complexity,
    className,
}: ComponentPreviewProps) {
    return (
        <motion.div
            whileHover={{ y: -2 }}
            className={cn(
                'rounded-2xl border border-white/10 bg-surface/50 p-5 hover:border-[var(--primary)]/30 transition-all duration-300 cursor-pointer group',
                className
            )}
        >
            <div className="flex items-start justify-between mb-3">
                <div>
                    <h4 className="font-semibold text-white group-hover:text-[var(--primary)] transition-colors">
                        {name}
                    </h4>
                    <span className="text-xs text-gray-500 uppercase tracking-wider">{type}</span>
                </div>
                <div className="flex gap-1">
                    <button className="p-1.5 rounded-lg hover:bg-white/5 text-gray-500 hover:text-white transition-colors">
                        <Eye className="w-3.5 h-3.5" />
                    </button>
                    <button className="p-1.5 rounded-lg hover:bg-white/5 text-gray-500 hover:text-white transition-colors">
                        <Code className="w-3.5 h-3.5" />
                    </button>
                </div>
            </div>

            <p className="text-sm text-gray-400 mb-3 line-clamp-2">{description}</p>

            <div className="flex items-center gap-2 flex-wrap">
                {complexity && (
                    <span className={cn(
                        'text-xs px-2 py-0.5 rounded-full',
                        complexity === 'simple' && 'bg-green-500/10 text-green-400',
                        complexity === 'medium' && 'bg-yellow-500/10 text-yellow-400',
                        complexity === 'complex' && 'bg-red-500/10 text-red-400'
                    )}>
                        {complexity}
                    </span>
                )}
                {keywords?.slice(0, 3).map((kw, i) => (
                    <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-500">
                        {kw}
                    </span>
                ))}
            </div>
        </motion.div>
    );
}