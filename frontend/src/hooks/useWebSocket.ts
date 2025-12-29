import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  url: string;
  enabled?: boolean;
  onOpen?: () => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (error: Event) => void;
}

/**
 * Low-level WebSocket hook for managing connection lifecycle.
 * Does NOT contain business logic - just handles connection, send, and receive.
 */
export function useWebSocket({
  url,
  enabled = true,
  onOpen,
  onClose,
  onError,
}: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<MessageEvent | null>(null);

  // Store callbacks in refs to avoid reconnecting when they change
  const onOpenRef = useRef(onOpen);
  const onCloseRef = useRef(onClose);
  const onErrorRef = useRef(onError);

  useEffect(() => {
    onOpenRef.current = onOpen;
    onCloseRef.current = onClose;
    onErrorRef.current = onError;
  }, [onOpen, onClose, onError]);

  // Connect to WebSocket
  useEffect(() => {
    if (!enabled) {
      return;
    }

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[useWebSocket] Connected to:', url);
      setIsConnected(true);
      onOpenRef.current?.();
    };

    ws.onmessage = (event) => {
      setLastMessage(event);
    };

    ws.onerror = (error) => {
      console.error('[useWebSocket] Error:', error);
      console.error('[useWebSocket] ReadyState:', ws.readyState);
      console.error('[useWebSocket] URL:', url);
      setIsConnected(false);
      onErrorRef.current?.(error);
    };

    ws.onclose = (event) => {
      console.log('[useWebSocket] Disconnected from:', url);
      console.log(
        '[useWebSocket] Close code:',
        event.code,
        'Reason:',
        event.reason
      );
      console.log('[useWebSocket] Was clean close:', event.wasClean);
      setIsConnected(false);
      onCloseRef.current?.(event);
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [enabled, url]); // Only reconnect when enabled or url changes

  // Send message (generic)
  const send = useCallback((data: string | object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      console.log('Websocket data message', message);
      wsRef.current.send(message);
    } else {
      console.warn('[useWebSocket] Cannot send - connection not open');
    }
  }, []);

  return {
    isConnected,
    lastMessage,
    send,
  };
}
