import { NextResponse } from 'next/server';
import { BackendBridge } from '@/lib/backend';

export async function GET() {
    try {
        const status = BackendBridge.getStatus();
        return NextResponse.json(status);
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
