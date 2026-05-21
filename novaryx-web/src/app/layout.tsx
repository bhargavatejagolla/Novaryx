import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Navbar } from '@/components/layout/Navbar';
import { ThemeProvider } from '@/components/layout/ThemeProvider';
import { GenerationProvider } from '@/context/GenerationContext';
import '@/styles/globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
    title: 'NOVARYX - AI-Powered Application Builder',
    description: 'Build complete, production-ready web applications from a single prompt. Powered by AI.',
    keywords: ['AI', 'website builder', 'app generator', 'React', 'Next.js', 'AI code generator'],
    openGraph: {
        title: 'NOVARYX - AI Application Builder',
        description: 'Build production-ready apps from a single prompt',
        type: 'website',
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <body className={`${inter.variable} font-sans bg-[#03050a] text-white antialiased`}>
                {/* Premium Global Mesh Gradient Background */}
                <div className="fixed inset-0 overflow-hidden pointer-events-none z-[-1]">
                    <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/20 blur-[120px] rounded-full mix-blend-screen animate-blob" />
                    <div className="absolute top-[20%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 blur-[120px] rounded-full mix-blend-screen animate-blob" style={{ animationDelay: '2s' }} />
                    <div className="absolute bottom-[-20%] left-[20%] w-[50%] h-[50%] bg-pink-600/10 blur-[120px] rounded-full mix-blend-screen animate-blob" style={{ animationDelay: '4s' }} />
                    
                    {/* Subtle Grid Overlay */}
                    <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
                </div>

                <ThemeProvider>
                    <GenerationProvider>
                        <Navbar />
                        <main className="pt-16 min-h-screen relative z-0">
                            {children}
                        </main>
                    </GenerationProvider>
                </ThemeProvider>
            </body>
        </html>
    );
}