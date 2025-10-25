'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { ObjectTypes } from '@/openapi/managerLab.schemas';

export interface Viewer {
  user_id: string;
  name: string;
  is_typing: boolean;
}

interface WebSocketMessage {
  type: string;
  user_id?: string;
  viewers?: Viewer[];
  message_id?: number;
  thread_id?: number;
  timestamp?: number;
  is_typing?: boolean;
}

interface UseThreadConnectionOptions {
  threadableType: ObjectTypes;
  threadableId: string;
  enabled?: boolean;
  onMessageUpdate?: () => void;
}

export function useThreadConnection({
  threadableType,
  threadableId,
  enabled = true,
  onMessageUpdate,
}: UseThreadConnectionOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const [viewers, setViewers] = useState<Viewer[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // Connect to WebSocket
  useEffect(() => {
    if (!enabled) return;

    // Use backend URL from environment variable, fallback to localhost:8000
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const protocol = backendUrl.startsWith('https') ? 'wss:' : 'ws:';
    const host = backendUrl.replace(/^https?:\/\//, '');
    const wsUrl = `${protocol}//${host}/ws/threads/${threadableType}/${threadableId}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      // Mark thread as read when connecting
      ws.send(JSON.stringify({ type: 'mark_read' }));
    };

    ws.onmessage = (event) => {
      const notification: WebSocketMessage = JSON.parse(event.data);
      console.log('WebSocket notification:', notification);

      switch (notification.type) {
        case 'user_joined':
        case 'typing_update':
          if (notification.viewers) {
            setViewers(notification.viewers);
          }
          break;

        case 'new_message':
        case 'message_updated':
        case 'message_deleted':
          // Notify consumer to refetch messages
          onMessageUpdate?.();
          break;

        case 'pong':
          // Handle pong response
          break;

        case 'marked_read':
          // Thread marked as read confirmation
          break;

        default:
          console.log('Unknown notification type:', notification.type);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      console.error('WebSocket readyState:', ws.readyState);
      console.error('WebSocket URL:', wsUrl);
      setIsConnected(false);
    };

    ws.onclose = (event) => {
      console.log('WebSocket disconnected');
      console.log('Close code:', event.code, 'Reason:', event.reason);
      console.log('Was clean close:', event.wasClean);
      setIsConnected(false);
      setViewers([]);
    };

    // Send ping every 30 seconds to keep connection alive
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
      }
    }, 30000);

    return () => {
      clearInterval(pingInterval);
      ws.close();
      wsRef.current = null;
    };
  }, [enabled, threadableType, threadableId, onMessageUpdate]);

  // Send typing indicator
  const sendTypingIndicator = useCallback((isTyping: boolean) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({ type: 'typing', is_typing: isTyping })
      );
    }
  }, []);

  return {
    viewers,
    isConnected,
    sendTypingIndicator,
  };
}
