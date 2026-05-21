import { NextRequest, NextResponse } from 'next/server';
import { BackendBridge } from '@/lib/backend';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { prompt, theme } = body;

        if (!prompt || typeof prompt !== 'string' || prompt.trim().length < 5) {
            return NextResponse.json(
                { error: 'Prompt must be at least 5 characters', success: false },
                { status: 400 }
            );
        }

        console.log(`\n📝 NOVARYX generate request: "${prompt.slice(0, 80)}"`);

        // Run the full Python generation pipeline (LLM enabled – uses Groq by default)
        const result = BackendBridge.generate(prompt.trim(), theme);

        if (!result.success) {
            return NextResponse.json(
                {
                    success: false,
                    error: (result.errors?.[0]) || 'Generation pipeline failed',
                    errors: result.errors || [],
                },
                { status: 500 }
            );
        }

        return NextResponse.json({
            success: true,
            project_name: result.project_name || 'NOVARYX Project',
            files: result.files || [],
            components: result.components || [],
            component_count: result.componentCount ?? result.components?.length ?? 0,
            errors: result.errors || [],
        });
    } catch (error: any) {
        console.error('❌ API generate error:', error);
        return NextResponse.json(
            { error: error.message || 'Internal server error', success: false },
            { status: 500 }
        );
    }
}