'use client';

import { motion } from 'framer-motion';
import { Sun, Moon, Palette } from 'lucide-react';
import { COLOR_PRESETS, FONT_OPTIONS } from '@/lib/constants';
import { cn } from '@/lib/utils';

import { ThemeConfig } from '@/components/layout/ThemeProvider';

interface ThemeCustomizerProps {
    theme: ThemeConfig;
    onThemeChange: (updates: Partial<ThemeConfig>) => void;
    onToggleMode: () => void;
    className?: string;
}

export function ThemeCustomizer({ theme, onThemeChange, onToggleMode, className }: ThemeCustomizerProps) {
    return (
        <div className={cn('space-y-6', className)}>
            {/* Mode Toggle */}
            <div>
                <label className="text-xs text-gray-500 uppercase tracking-wider mb-3 block">Mode</label>
                <div className="flex gap-2">
                    <button
                        onClick={onToggleMode}
                        className={cn(
                            'flex-1 flex items-center justify-center gap-2 p-3 rounded-xl border transition-all duration-200',
                            theme.mode === 'dark'
                                ? 'border-[var(--primary)] bg-[var(--primary)]/10 text-white'
                                : 'border-white/10 bg-surface/50 text-gray-500 hover:border-white/20'
                        )}
                    >
                        <Moon className="w-4 h-4" />
                        Dark
                    </button>
                    <button
                        onClick={onToggleMode}
                        className={cn(
                            'flex-1 flex items-center justify-center gap-2 p-3 rounded-xl border transition-all duration-200',
                            theme.mode === 'light'
                                ? 'border-[var(--primary)] bg-[var(--primary)]/10 text-white'
                                : 'border-white/10 bg-surface/50 text-gray-500 hover:border-white/20'
                        )}
                    >
                        <Sun className="w-4 h-4" />
                        Light
                    </button>
                </div>
            </div>

            {/* Color Presets */}
            <div>
                <label className="text-xs text-gray-500 uppercase tracking-wider mb-3 block">Primary Color</label>
                <div className="grid grid-cols-4 gap-2">
                    {COLOR_PRESETS.map((color) => (
                        <motion.button
                            key={color.value}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => onThemeChange({ primary: color.value })}
                            className={cn(
                                'w-full aspect-square rounded-xl transition-all duration-200',
                                theme.primary === color.value
                                    ? 'ring-2 ring-white ring-offset-2 ring-offset-background scale-110'
                                    : 'hover:scale-105'
                            )}
                            style={{ backgroundColor: color.value }}
                            title={color.name}
                        />
                    ))}
                </div>
                <div className="mt-2 flex items-center gap-2">
                    <Palette className="w-4 h-4 text-gray-500" />
                    <input
                        type="color"
                        value={theme.primary}
                        onChange={(e) => onThemeChange({ primary: e.target.value })}
                        className="w-8 h-8 rounded-lg cursor-pointer border-0 bg-transparent"
                    />
                    <input
                        type="text"
                        value={theme.primary}
                        onChange={(e) => onThemeChange({ primary: e.target.value })}
                        className="flex-1 px-3 py-1.5 text-sm rounded-lg bg-white/5 border border-white/10 text-white font-mono"
                    />
                </div>
            </div>

            {/* Font */}
            <div>
                <label className="text-xs text-gray-500 uppercase tracking-wider mb-3 block">Font</label>
                <div className="grid grid-cols-1 gap-1">
                    {FONT_OPTIONS.map((font) => (
                        <button
                            key={font}
                            onClick={() => onThemeChange({ font })}
                            className={cn(
                                'text-left px-3 py-2 rounded-lg text-sm transition-all duration-200',
                                theme.font === font
                                    ? 'bg-[var(--primary)]/10 text-[var(--primary)] font-medium'
                                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                            )}
                            style={{ fontFamily: font }}
                        >
                            {font}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}