import { NextRequest, NextResponse } from 'next/server';

// Sync with Python theme engine
const currentTheme = {
    primary: '#6366f1',
    accent: '#06b6d4',
    mode: 'dark' as 'dark' | 'light',
    font: 'Inter',
    borderRadius: '12px',
    glassmorphism: true,
};

export async function GET() {
    return NextResponse.json({ ...currentTheme });
}

export async function POST(request: NextRequest) {
    try {
        const updates = await request.json();
        Object.assign(currentTheme, updates);

        // Also save to file for Python backend to read
        const fs = require('fs');
        const path = require('path');
        const configDir = path.join(
            process.env.HOME || process.env.USERPROFILE || '',
            'novaryx', 'config'
        );
        if (!fs.existsSync(configDir)) fs.mkdirSync(configDir, { recursive: true });
        fs.writeFileSync(
            path.join(configDir, 'active_theme.json'),
            JSON.stringify(currentTheme, null, 2)
        );

        return NextResponse.json({ success: true, theme: currentTheme });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}