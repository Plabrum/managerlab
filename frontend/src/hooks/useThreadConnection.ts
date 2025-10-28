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
          // User joined - replace entire viewers list
          if (notification.viewers) {
            setViewers(notification.viewers);
          }
          break;

        case 'user_left':
          // User left - remove from viewers list
          if (notification.user_id !== undefined) {
            setViewers((prevViewers) =>
              prevViewers.filter(
                (viewer) => viewer.user_id !== notification.user_id
              )
            );
          }
          break;

        case 'typing_update':
          // Update specific user's typing status
          if (
            notification.user_id !== undefined &&
            notification.is_typing !== undefined
          ) {
            setViewers((prevViewers) =>
              prevViewers.map((viewer) =>
                viewer.user_id === notification.user_id
                  ? { ...viewer, is_typing: notification.is_typing! }
                  : viewer
              )
            );
          }
          break;

        case 'message_update':
          // Message was created, updated, or deleted - refetch messages
          onMessageUpdate?.();
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

    return () => {
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
