import { NextRequest, NextResponse } from 'next/server';
import { spawnSync } from 'child_process';
import path from 'path';
import fs from 'fs';
import os from 'os';

export async function GET(request: NextRequest) {
    try {
        const url = new URL(request.url);
        const project = url.searchParams.get('project') || 'latest';
        
        const exportsDir = path.join(process.env.HOME || process.env.USERPROFILE || '', 'novaryx', 'exports');
        
        if (!fs.existsSync(exportsDir)) {
            return new NextResponse('No exported projects found.', { status: 404 });
        }
        
        // Find latest project folder
        const dirs = fs.readdirSync(exportsDir)
            .map(name => ({ name, stat: fs.statSync(path.join(exportsDir, name)) }))
            .filter(grid => grid.stat.isDirectory() && grid.name !== 'archives')
            .sort((a, b) => b.stat.mtime.getTime() - a.stat.mtime.getTime());
            
        if (dirs.length === 0) {
            return new NextResponse('No exported projects found.', { status: 404 });
        }
        
        const targetProjectDir = path.join(exportsDir, dirs[0].name);
        
        // Create a zip using Windows tar.exe (available on Windows 10+)
        const zipPath = path.join(os.tmpdir(), `${dirs[0].name}.zip`);
        
        // Remove existing zip if any
        if (fs.existsSync(zipPath)) fs.unlinkSync(zipPath);
        
        // Use PowerShell Compress-Archive for reliable zipping on Windows
        const psCommand = `Compress-Archive -Path "${targetProjectDir}\\*" -DestinationPath "${zipPath}" -Force`;
        spawnSync('powershell.exe', ['-Command', psCommand], { stdio: 'ignore' });
        
        if (!fs.existsSync(zipPath)) {
            return new NextResponse('Failed to generate zip archive.', { status: 500 });
        }
        
        const fileBuffer = fs.readFileSync(zipPath);
        
        // Clean up
        try { fs.unlinkSync(zipPath); } catch (e) {}

        return new NextResponse(fileBuffer, {
            headers: {
                'Content-Type': 'application/zip',
                'Content-Disposition': `attachment; filename="${dirs[0].name}.zip"`,
            }
        });
        
    } catch (error: any) {
        console.error('Download error:', error);
        return new NextResponse(error.message, { status: 500 });
    }
}
