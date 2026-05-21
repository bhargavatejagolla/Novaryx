import { NextRequest } from 'next/server';
import { BackendBridge } from '@/lib/backend';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { prompt, projectId, customPath } = body;

        if (!prompt || typeof prompt !== 'string' || prompt.trim().length < 5) {
            return new Response(
                JSON.stringify({ error: 'Prompt must be at least 5 characters' }),
                {
                    status: 400,
                    headers: { 'Content-Type': 'application/json' },
                }
            );
        }

        const encoder = new TextEncoder();
        const customStream = new ReadableStream({
            start(controller) {
                let isClosed = false;
                try {

                    BackendBridge.generateStream(
                        prompt.trim(),
                        { projectId, customPath },
                        (progressMsg) => {
                            if (isClosed) return;
                            try {
                                controller.enqueue(
                                    encoder.encode(`data: ${JSON.stringify({ type: 'progress', message: progressMsg })}\n\n`)
                                );
                            } catch (e) {
                                isClosed = true;
                            }
                        },
                        (result) => {
                            if (isClosed) return;
                            try {
                                controller.enqueue(
                                    encoder.encode(`data: ${JSON.stringify({ type: 'result', result })}\n\n`)
                                );
                                controller.close();
                            } catch (e) {
                                // already closed
                            }
                            isClosed = true;
                        },
                        (errorMsg) => {
                            if (isClosed) return;
                            try {
                                controller.enqueue(
                                    encoder.encode(`data: ${JSON.stringify({ type: 'error', message: errorMsg })}\n\n`)
                                );
                                controller.close();
                            } catch (e) {
                                // already closed
                            }
                            isClosed = true;
                        },
                        request.signal
                    );
                } catch (err: any) {
                    if (!isClosed) {
                        try {
                            controller.enqueue(
                                encoder.encode(`data: ${JSON.stringify({ type: 'error', message: err.message })}\n\n`)
                            );
                            controller.close();
                        } catch (e) {}
                        isClosed = true;
                    }
                }
            }
        });

        return new Response(customStream, {
            headers: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            },
        });
    } catch (err: any) {
        return new Response(
            JSON.stringify({ error: err.message || 'Internal server error' }),
            {
                status: 500,
                headers: { 'Content-Type': 'application/json' },
            }
        );
    }
}
