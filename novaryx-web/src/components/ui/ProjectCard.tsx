'use client';

import { motion } from 'framer-motion';
import { Calendar, FileText, Box, ArrowRight, CheckCircle2, XCircle } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface ProjectCardProps {
    project: {
        name: string;
        type: string;
        components: string[];
        files: number;
        success: boolean;
        quality: number;
        created: string;
        primaryColor?: string;
    };
    onClick?: () => void;
    className?: string;
}

export function ProjectCard({ project, onClick, className }: ProjectCardProps) {
    return (
        <motion.div
            whileHover={{ y: -4 }}
            onClick={onClick}
            className={cn(
                'rounded-2xl border border-white/10 bg-surface/50 p-5 hover:border-[var(--primary)]/30 transition-all duration-300 cursor-pointer group',
                className
            )}
        >
            {/* Color bar */}
            {project.primaryColor && (
                <div
                    className="h-1 rounded-full mb-4"
                    style={{ backgroundColor: project.primaryColor }}
                />
            )}

            {/* Status + Name */}
            <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold text-white group-hover:text-[var(--primary)] transition-colors">
                    {project.name}
                </h3>
                {project.success ? (
                    <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />
                ) : (
                    <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                )}
            </div>

            {/* Type */}
            <span className="text-xs text-gray-500 uppercase tracking-wider">{project.type}</span>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-2 mt-4 mb-3">
                <div className="flex items-center gap-1.5 text-sm text-gray-400">
                    <FileText className="w-3.5 h-3.5" />
                    {project.files} files
                </div>
                <div className="flex items-center gap-1.5 text-sm text-gray-400">
                    <Box className="w-3.5 h-3.5" />
                    {project.components.length} comps
                </div>
            </div>

            {/* Components preview */}
            <div className="flex flex-wrap gap-1 mb-3">
                {project.components.slice(0, 4).map((comp, i) => (
                    <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-500">
                        {comp}
                    </span>
                ))}
                {project.components.length > 4 && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-600">
                        +{project.components.length - 4}
                    </span>
                )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between pt-3 border-t border-white/5">
                <div className="flex items-center gap-1 text-xs text-gray-600">
                    <Calendar className="w-3 h-3" />
                    {formatDate(project.created)}
                </div>
                <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-[var(--primary)] transition-colors" />
            </div>
        </motion.div>
    );
}