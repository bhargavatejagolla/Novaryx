import { NextRequest, NextResponse } from 'next/server';
import { BackendBridge } from '@/lib/backend';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { name, code } = body;

        if (!name || typeof name !== 'string' || name.trim().length === 0) {
            return NextResponse.json(
                { error: 'Component name is required', success: false },
                { status: 400 }
            );
        }

        if (!code || typeof code !== 'string' || code.trim().length === 0) {
            return NextResponse.json(
                { error: 'Component code is required', success: false },
                { status: 400 }
            );
        }

        console.log(`\n🧠 NOVARYX Ingestion: Learning "${name}"...`);

        // Run the Python ingestion pipeline
        const result = BackendBridge.ingestComponent(name.trim(), code.trim());

        if (!result.success) {
            return NextResponse.json(
                {
                    success: false,
                    error: result.error || 'Ingestion failed',
                },
                { status: 500 }
            );
        }

        return NextResponse.json({
            success: true,
            result: result.result,
        });
    } catch (error: any) {
        console.error('❌ API ingestion error:', error);
        return NextResponse.json(
            { error: error.message || 'Internal server error', success: false },
            { status: 500 }
        );
    }
}
