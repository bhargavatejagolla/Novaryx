"""
NOVARYX - AI Scaffold Generator
Injects a fully functional Groq-powered AI Assistant into generated projects.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("novaryx.ai_scaffold")

# -----------------------------------------------------------------------------
# 1. API Route Template (Groq Streaming)
# -----------------------------------------------------------------------------
API_ROUTE_TEMPLATE = """import { NextResponse } from 'next/server';
import { Groq } from 'groq-sdk';

const groq = new Groq({
    apiKey: process.env.GROQ_API_KEY,
});

export async function POST(req: Request) {
    try {
        const { messages, context } = await req.json();

        if (!process.env.GROQ_API_KEY) {
            return NextResponse.json(
                { error: 'GROQ_API_KEY is not set in environment variables.' },
                { status: 500 }
            );
        }

        const systemMessage = {
            role: 'system',
            content: `You are an intelligent embedded assistant for this application.
You are helpful, concise, and knowledgeable about the application's domain.
Context about current state: ${context || 'None provided'}
Respond using Markdown formatting.`
        };

        const chatCompletion = await groq.chat.completions.create({
            messages: [systemMessage, ...messages],
            model: 'llama-3.3-70b-versatile',
            temperature: 0.5,
            max_tokens: 1024,
            stream: false, // Set to true for SSE streaming if supported by frontend
        });

        return NextResponse.json({
            message: chatCompletion.choices[0]?.message?.content || 'No response',
        });

    } catch (error: any) {
        console.error('Chat API Error:', error);
        return NextResponse.json(
            { error: error.message || 'Internal server error' },
            { status: 500 }
        );
    }
}
"""

# -----------------------------------------------------------------------------
# 2. React Component Template (Floating Assistant)
# -----------------------------------------------------------------------------
AI_ASSISTANT_TEMPLATE = """'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function AiAssistant() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([
        { role: 'assistant', content: 'Hello! I am your AI assistant. How can I help you today?' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMsg = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsLoading(true);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: messages.concat({ role: 'user', content: userMsg }).slice(-5), // Send last 5 msgs
                    context: `Current Path: ${typeof window !== 'undefined' ? window.location.pathname : 'Unknown'}`
                })
            });

            const data = await res.json();
            
            if (!res.ok) throw new Error(data.error || 'Failed to get response');

            setMessages(prev => [...prev, { role: 'assistant', content: data.message }]);
        } catch (err: any) {
            setMessages(prev => [...prev, { role: 'assistant', content: `⚠️ Error: ${err.message}` }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50">
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="absolute bottom-16 right-0 w-80 sm:w-96 h-[500px] bg-gray-900 border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
                    >
                        {/* Header */}
                        <div className="p-4 bg-gray-800/50 border-b border-white/5 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                                <span className="font-medium text-white">AI Assistant</span>
                            </div>
                            <button 
                                onClick={() => setIsOpen(false)}
                                className="text-gray-400 hover:text-white transition-colors"
                            >
                                ✕
                            </button>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {messages.map((msg, i) => (
                                <div 
                                    key={i} 
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div 
                                        className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
                                            msg.role === 'user' 
                                                ? 'bg-indigo-600 text-white rounded-tr-sm' 
                                                : 'bg-gray-800 text-gray-200 border border-white/5 rounded-tl-sm'
                                        }`}
                                    >
                                        {msg.content}
                                    </div>
                                </div>
                            ))}
                            {isLoading && (
                                <div className="flex justify-start">
                                    <div className="bg-gray-800 text-gray-200 border border-white/5 rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1">
                                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" />
                                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input */}
                        <div className="p-4 border-t border-white/5 bg-gray-900">
                            <form onSubmit={handleSend} className="relative">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Ask anything..."
                                    className="w-full bg-gray-800 border border-white/10 rounded-xl pl-4 pr-12 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition-colors"
                                />
                                <button
                                    type="submit"
                                    disabled={!input.trim() || isLoading}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
                                >
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className="w-5 h-5">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
                                    </svg>
                                </button>
                            </form>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Toggle Button */}
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsOpen(!isOpen)}
                className={`w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-colors ${
                    isOpen ? 'bg-gray-800 text-white border border-white/10' : 'bg-indigo-600 text-white hover:bg-indigo-500'
                }`}
            >
                {isOpen ? (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className="w-6 h-6">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                ) : (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className="w-6 h-6">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                )}
            </motion.button>
        </div>
    );
}
"""

class AiScaffoldGenerator:
    """Injects AI capabilities into generated projects."""

    def __init__(self):
        pass

    def inject_scaffold(self, all_files: Dict[str, str], env_vars: Dict[str, str]):
        """Injects API routes, components, and updates dependencies."""
        
        # 1. Add API Route
        all_files["src/app/api/chat/route.ts"] = API_ROUTE_TEMPLATE
        
        # 2. Add Component
        all_files["src/components/AiAssistant.tsx"] = AI_ASSISTANT_TEMPLATE
        
        # 3. Modify Layout/App.tsx to include the assistant globally
        # Depending on whether it's Next.js App Router (layout.tsx) or Pages Router (App.tsx)
        layout_files = ["src/app/layout.tsx", "src/App.tsx"]
        injected = False
        
        for lf in layout_files:
            if lf in all_files:
                content = all_files[lf]
                
                # Check if we can safely inject it
                if "export default function" in content and "</body>" in content:
                    # Next.js App Router
                    content = content.replace(
                        "export default function", 
                        "import AiAssistant from '@/components/AiAssistant';\n\nexport default function"
                    )
                    content = content.replace(
                        "</body>", 
                        "  <AiAssistant />\n      </body>"
                    )
                    all_files[lf] = content
                    injected = True
                    break
                elif "export default function" in content and "</main>" in content:
                    content = content.replace(
                        "export default function", 
                        "import AiAssistant from '../components/AiAssistant';\n\nexport default function"
                    )
                    content = content.replace(
                        "</main>", 
                        "  <AiAssistant />\n      </main>"
                    )
                    all_files[lf] = content
                    injected = True
                    break
                elif "export default function" in content and "</ThemeProvider>" in content:
                    content = content.replace(
                        "export default function", 
                        "import AiAssistant from './components/AiAssistant';\n\nexport default function"
                    )
                    content = content.replace(
                        "</ThemeProvider>", 
                        "  <AiAssistant />\n    </ThemeProvider>"
                    )
                    all_files[lf] = content
                    injected = True
                    break
                elif "export default function" in content and "</BrowserRouter>" in content:
                    content = content.replace(
                        "export default function", 
                        "import AiAssistant from './components/AiAssistant';\n\nexport default function"
                    )
                    content = content.replace(
                        "</BrowserRouter>", 
                        "  <AiAssistant />\n    </BrowserRouter>"
                    )
                    all_files[lf] = content
                    injected = True
                    break

        # 4. Modify package.json to include groq-sdk
        if "package.json" in all_files:
            pkg = all_files["package.json"]
            if '"dependencies": {' in pkg and "groq-sdk" not in pkg:
                all_files["package.json"] = pkg.replace(
                    '"dependencies": {', 
                    '"dependencies": {\n    "groq-sdk": "^0.3.2",'
                )

        # 5. Add to environment variables
        env_vars["GROQ_API_KEY"] = "your_groq_api_key_here"
        
        env_content = "\n".join([f"{k}={v}" for k, v in env_vars.items()])
        
        if ".env.local" in all_files:
            all_files[".env.local"] += "\n\n" + env_content
        else:
            all_files[".env.local"] = env_content
            
        if ".env.example" in all_files:
            all_files[".env.example"] += "\n\nGROQ_API_KEY=your_groq_api_key_here"
        else:
            all_files[".env.example"] = "GROQ_API_KEY=your_groq_api_key_here"
        
        if injected:
            logger.info("Successfully injected AI Assistant scaffold into project layout.")
        else:
            logger.warning("Could not automatically inject AiAssistant into layout files. Added component only.")

