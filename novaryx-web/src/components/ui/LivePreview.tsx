'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Monitor, Smartphone, Tablet, ExternalLink, RotateCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LivePreviewProps {
    projectUrl?: string;
    className?: string;
}

type Viewport = 'desktop' | 'tablet' | 'mobile';

const viewportSizes: Record<Viewport, string> = {
    desktop: 'w-full',
    tablet: 'w-[768px]',
    mobile: 'w-[375px]',
};

export function LivePreview({ projectUrl = 'http://localhost:3000', className }: LivePreviewProps) {
    const [viewport, setViewport] = useState<Viewport>('desktop');
    const [key, setKey] = useState(0);

    return (
        <div className={cn('rounded-2xl border border-white/10 overflow-hidden', className)}>
            {/* Toolbar */}
            <div className="flex items-center justify-between px-4 py-2 bg-surface border-b border-white/10">
                <div className="flex items-center gap-3">
                    <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500/80" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                        <div className="w-3 h-3 rounded-full bg-green-500/80" />
                    </div>
                    <span className="text-xs text-gray-500 ml-2">{projectUrl}</span>
                </div>
                <div className="flex items-center gap-1">
                    <button
                        onClick={() => setViewport('mobile')}
                        className={cn(
                            'p-1.5 rounded-lg transition-colors',
                            viewport === 'mobile' ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-white'
                        )}
                    >
                        <Smartphone className="w-4 h-4" />
                    </button>
                    <button
                        onClick={() => setViewport('tablet')}
                        className={cn(
                            'p-1.5 rounded-lg transition-colors',
                            viewport === 'tablet' ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-white'
                        )}
                    >
                        <Tablet className="w-4 h-4" />
                    </button>
                    <button
                        onClick={() => setViewport('desktop')}
                        className={cn(
                            'p-1.5 rounded-lg transition-colors',
                            viewport === 'desktop' ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-white'
                        )}
                    >
                        <Monitor className="w-4 h-4" />
                    </button>
                    <div className="w-px h-4 bg-white/10 mx-2" />
                    <button
                        onClick={() => setKey((k) => k + 1)}
                        className="p-1.5 rounded-lg text-gray-500 hover:text-white transition-colors"
                    >
                        <RotateCw className="w-4 h-4" />
                    </button>
                    <a
                        href={projectUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 rounded-lg text-gray-500 hover:text-white transition-colors"
                    >
                        <ExternalLink className="w-4 h-4" />
                    </a>
                </div>
            </div>

            {/* Preview */}
            <div className="flex justify-center bg-[#1a1a2e] p-4 min-h-[500px] overflow-auto">
                <motion.div
                    key={key}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className={cn(
                        'bg-white rounded-lg overflow-hidden transition-all duration-300',
                        viewportSizes[viewport]
                    )}
                >
                    <iframe
                        src={projectUrl}
                        className="w-full h-[600px] border-0"
                        title="Live Preview"
                    />
                </motion.div>
            </div>
        </div>
    );
}