import { useState, useEffect, useRef, useCallback } from 'react';

const WS_URL      = 'ws://127.0.0.1:8001/ws';
const COMMAND_URL = 'http://127.0.0.1:8001/command';
const STOP_URL    = 'http://127.0.0.1:8001/stop';
const RECONNECT_MS = 3000;

/**
 * useDavidAI — connects the React frontend to the David AI FastAPI backend.
 *
 * Returns:
 *   isConnected   — boolean, true when WebSocket is open
 *   davidResponse — last text response from David
 *   userInput     — last user input echoed back by David
 *   status        — backend status string  (e.g. "Listening", "Ready")
 *   sendCommand   — fn(text: string) → POSTs text command to backend
 */
const useDavidAI = () => {
    const [isConnected, setIsConnected]     = useState(false);
    const [davidResponse, setDavidResponse] = useState('');
    const [userInput, setUserInput]         = useState('');
    const [status, setStatus]               = useState('Disconnected');
    const [ragStatus, setRagStatus]         = useState({ is_indexing: false, count: 0 });

    const wsRef        = useRef(null);
    const reconnectRef = useRef(null);
    const mountedRef   = useRef(true);

    const fetchRagStatus = useCallback(async () => {
        if (!mountedRef.current) return;
        try {
            const res = await fetch('http://127.0.0.1:8001/api/rag/status');
            const data = await res.json();
            setRagStatus(data);
        } catch (_) {}
    }, []);

    const triggerScan = useCallback(async () => {
        try {
            await fetch('http://127.0.0.1:8001/api/rag/index', { method: 'POST' });
            fetchRagStatus();
        } catch (_) {}
    }, [fetchRagStatus]);

    // Poll RAG status every 10 seconds while connected
    useEffect(() => {
        if (isConnected) {
            const interval = setInterval(fetchRagStatus, 10000);
            fetchRagStatus();
            return () => clearInterval(interval);
        }
    }, [isConnected, fetchRagStatus]);

    const connect = useCallback(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

        try {
            const ws = new WebSocket(WS_URL);
            wsRef.current = ws;

            ws.onopen = () => {
                if (!mountedRef.current) return;
                setIsConnected(true);
                setStatus('Connected');
                if (reconnectRef.current) {
                    clearTimeout(reconnectRef.current);
                    reconnectRef.current = null;
                }
            };

            ws.onmessage = (evt) => {
                if (!mountedRef.current) return;
                try {
                    const msg = JSON.parse(evt.data);
                    const { event, payload } = msg;
                    if (event === 'response')    setDavidResponse(payload);
                    if (event === 'user_input')  setUserInput(payload);
                    if (event === 'status')      setStatus(payload);
                    if (event === 'shutdown')    setStatus('Shutting down…');
                } catch (_) {}
            };

            ws.onerror = () => {
                ws.close();
            };

            ws.onclose = () => {
                if (!mountedRef.current) return;
                setIsConnected(false);
                setStatus('Disconnected');
                // Auto-reconnect
                reconnectRef.current = setTimeout(connect, RECONNECT_MS);
            };

        } catch (_) {
            reconnectRef.current = setTimeout(connect, RECONNECT_MS);
        }
    }, []);

    useEffect(() => {
        mountedRef.current = true;
        connect();
        return () => {
            mountedRef.current = false;
            if (reconnectRef.current) clearTimeout(reconnectRef.current);
            if (wsRef.current) wsRef.current.close();
        };
    }, [connect]);

    const stopDavid = useCallback(async () => {
        try {
            await fetch(STOP_URL, { method: 'POST' });
        } catch (_) {}
    }, []);

    const sendCommand = useCallback(async (text) => {
        if (!text?.trim()) return;
        try {
            // Stop David from speaking before sending new command
            await stopDavid();
            await fetch(COMMAND_URL, {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ text: text.trim() }),
            });
        } catch (err) {
            console.warn('David AI backend unreachable:', err.message);
        }
    }, [stopDavid]);

    return { isConnected, davidResponse, userInput, status, ragStatus, sendCommand, stopDavid, triggerScan };
};

export default useDavidAI;
