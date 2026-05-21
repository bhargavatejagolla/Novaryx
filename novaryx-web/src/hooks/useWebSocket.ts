'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketMessage {
    event: string;
    data: any;
    timestamp: string;
}

export function useWebSocket() {
    const [connected, setConnected] = useState(false);
    const [messages, setMessages] = useState<WebSocketMessage[]>([]);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeout = useRef<NodeJS.Timeout>();

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const ws = new WebSocket('ws://localhost:9001');

        ws.onopen = () => {
            setConnected(true);
            ws.send(JSON.stringify({ type: 'subscribe', events: ['*'] }));
        };

        ws.onmessage = (event) => {
            try {
                const msg: WebSocketMessage = JSON.parse(event.data);
                setMessages((prev) => [...prev.slice(-100), msg]);
            } catch (e) {
                // Ignore parse errors
            }
        };

        ws.onclose = () => {
            setConnected(false);
            reconnectTimeout.current = setTimeout(connect, 3000);
        };

        ws.onerror = () => {
            ws.close();
        };

        wsRef.current = ws;
    }, []);

    useEffect(() => {
        connect();
        return () => {
            clearTimeout(reconnectTimeout.current);
            wsRef.current?.close();
        };
    }, [connect]);

    const send = useCallback((data: any) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
        }
    }, []);

    return { connected, messages, send };
}