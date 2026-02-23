/**
 * React Hook for Server-Sent Events (SSE) Log Streaming
 * Connects to the backend SSE endpoint and receives real-time logs
 */

import { useEffect, useRef, useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

interface LogStreamEvent {
  type: 'connected' | 'log' | 'process-started' | 'process-complete';
  level?: 'SUCCESS' | 'ERROR' | 'WARNING' | 'INFO';
  message?: string;
  endpoint?: string;
  success?: boolean;
  timestamp?: number;
  className?: string;
  error?: string;
}

export function useLogStream(addLog: (message: string) => void) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const maxReconnectAttempts = 5;

  useEffect(() => {
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      try {
        // Create SSE connection
        const eventSource = new EventSource(`${API_BASE_URL}/logs/stream`);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
          console.log('[SSE] Connected to log stream');
          setIsConnected(true);
          setReconnectAttempts(0);
        };

        eventSource.onmessage = (event) => {
          try {
            const data: LogStreamEvent = JSON.parse(event.data);

            if (data.type === 'connected') {
              console.log('[SSE] Connection confirmed');
            } else if (data.type === 'log') {
              // Add log message to UI
              if (data.message) {
                addLog(data.message);
              }
            } else if (data.type === 'process-started') {
              // Optional: Add start notification
              // addLog(`🚀 Starting ${data.endpoint}...`);
            } else if (data.type === 'process-complete') {
              // Optional: Add completion notification
              // addLog(data.success ? '✅ Process completed' : '❌ Process failed');
            }
          } catch (error) {
            console.error('[SSE] Failed to parse message:', error);
          }
        };

        eventSource.onerror = (error) => {
          console.error('[SSE] Connection error:', error);
          setIsConnected(false);
          eventSource.close();

          // Attempt to reconnect with exponential backoff
          if (reconnectAttempts < maxReconnectAttempts) {
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
            console.log(`[SSE] Reconnecting in ${delay}ms (attempt ${reconnectAttempts + 1}/${maxReconnectAttempts})`);

            reconnectTimeout = setTimeout(() => {
              setReconnectAttempts(prev => prev + 1);
              connect();
            }, delay);
          } else {
            console.error('[SSE] Max reconnection attempts reached');
          }
        };
      } catch (error) {
        console.error('[SSE] Failed to create EventSource:', error);
        setIsConnected(false);
      }
    };

    // Initial connection
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [addLog, reconnectAttempts]);

  return { isConnected };
}
