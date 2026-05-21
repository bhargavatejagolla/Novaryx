'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Zap, ArrowRight, X } from 'lucide-react';
import { EXAMPLE_PROMPTS } from '@/lib/constants';
import { cn } from '@/lib/utils';

interface PromptInputProps {
    onSubmit: (prompt: string) => void;
    loading?: boolean;
    className?: string;
    initialPrompt?: string;
    buttonText?: string;
    placeholder?: string;
}

export function PromptInput({ onSubmit, loading, className, initialPrompt, buttonText = 'Generate', placeholder = 'Describe what you want to build...' }: PromptInputProps) {
    const [prompt, setPrompt] = useState(initialPrompt || '');
    const [focused, setFocused] = useState(false);
    const [showExamples, setShowExamples] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
        }
    }, [prompt]);

    const handleSubmit = () => {
        if (prompt.trim() && !loading) {
            onSubmit(prompt.trim());
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const selectExample = (example: string) => {
        setPrompt(example);
        setShowExamples(false);
        textareaRef.current?.focus();
    };

    return (
        <div className={cn('w-full', className)}>
            <motion.div
                className={cn(
                    'relative rounded-2xl border transition-all duration-300',
                    focused
                        ? 'border-[var(--primary)] shadow-[0_0_30px_rgba(99,102,241,0.2)] bg-surface'
                        : 'border-white/10 bg-surface/50 hover:border-white/20'
                )}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <div className="flex items-start gap-3 p-4">
                    <div className="mt-2 text-[var(--primary)]">
                        <Sparkles className="w-5 h-5" />
                    </div>
                    <textarea
                        ref={textareaRef}
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        onFocus={() => { setFocused(true); setShowExamples(true); }}
                        onBlur={() => { setFocused(false); setTimeout(() => setShowExamples(false), 200); }}
                        onKeyDown={handleKeyDown}
                        placeholder={placeholder}
                        rows={2}
                        className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none outline-none text-lg leading-relaxed"
                        disabled={loading}
                    />
                    {prompt && (
                        <button
                            onClick={() => setPrompt('')}
                            className="mt-2 p-1 rounded-lg hover:bg-white/5 text-gray-500 hover:text-gray-300 transition-colors"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    )}
                </div>

                <div className="flex items-center justify-between px-4 pb-4">
                    <button
                        onClick={() => setShowExamples(!showExamples)}
                        className="text-xs text-gray-500 hover:text-gray-300 transition-colors flex items-center gap-1"
                    >
                        <Zap className="w-3 h-3" />
                        Examples
                    </button>
                    <motion.button
                        onClick={handleSubmit}
                        disabled={!prompt.trim() || loading}
                        className={cn(
                            'px-6 py-2.5 rounded-xl font-medium flex items-center gap-2 transition-all duration-200',
                            prompt.trim() && !loading
                                ? 'bg-[var(--primary)] text-white hover:shadow-[0_0_25px_rgba(99,102,241,0.4)]'
                                : 'bg-white/5 text-gray-600 cursor-not-allowed'
                        )}
                        whileHover={prompt.trim() && !loading ? { scale: 1.02 } : {}}
                        whileTap={prompt.trim() && !loading ? { scale: 0.98 } : {}}
                    >
                        {loading ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Working...
                            </>
                        ) : (
                            <>
                                {buttonText}
                                <ArrowRight className="w-4 h-4" />
                            </>
                        )}
                    </motion.button>
                </div>
            </motion.div>

            <AnimatePresence>
                {showExamples && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2"
                    >
                        {EXAMPLE_PROMPTS.slice(0, 4).map((example, i) => (
                            <button
                                key={i}
                                onClick={() => selectExample(example)}
                                className="text-left p-3 rounded-xl bg-surface/50 border border-white/5 text-sm text-gray-400 hover:text-white hover:border-[var(--primary)]/30 transition-all duration-200"
                            >
                                {example.length > 80 ? example.slice(0, 80) + '...' : example}
                            </button>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}