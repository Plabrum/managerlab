import { useEffect, useState, useCallback, useMemo } from 'react';
import { useWebSocket } from './useWebSocket';
import { ObjectTypes } from '@/openapi/ariveAPI.schemas';
import {
  ThreadSocketMessageType,
  type ServerMessage,
  type ClientMessage,
  type Viewer,
} from '@/types/websocket';

interface UseThreadConnectionOptions {
  threadableType: ObjectTypes;
  threadableId: string;
  enabled?: boolean;
  onMessageUpdate?: () => void;
}

/**
 * High-level hook for thread websocket connection.
 * Manages viewer presence, typing indicators, and message updates.
 */
export function useThreadConnection({
  threadableType,
  threadableId,
  enabled = true,
  onMessageUpdate,
}: UseThreadConnectionOptions) {
  // Build WebSocket URL
  const wsUrl = useMemo(() => {
    const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const protocol = backendUrl.startsWith('https') ? 'wss:' : 'ws:';
    const host = backendUrl.replace(/^https?:\/\//, '');
    return `${protocol}//${host}/ws/threads/${threadableType}/${threadableId}`;
  }, [threadableType, threadableId]);

  // Low-level websocket connection
  const { isConnected, lastMessage, send } = useWebSocket({
    url: wsUrl,
    enabled,
    onOpen: () => {
      // Mark thread as read when connecting
      send({
        message_type: ThreadSocketMessageType.MARK_READ,
      } as ClientMessage);
    },
    onClose: () => {
      setViewers([]);
    },
  });

  // Viewer state management
  const [viewers, setViewers] = useState<Viewer[]>([]);

  // User name cache (user_id → name)
  const [userNameCache, setUserNameCache] = useState<Map<string, string>>(
    new Map()
  );

  // Track page visibility for auto-marking as read
  const [isPageVisible, setIsPageVisible] = useState(
    typeof document !== 'undefined'
      ? document.visibilityState === 'visible'
      : true
  );

  // Listen for page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsPageVisible(document.visibilityState === 'visible');
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  // Process incoming messages
  useEffect(() => {
    if (!lastMessage) return;

    const message: ServerMessage = JSON.parse(lastMessage.data);
    console.log('[useThreadConnection] Message:', message);

    // Helper: Get or create viewer with cached name
    const getViewerFromId = (userId: string): Viewer => {
      const cachedName = userNameCache.get(userId);
      return {
        user_id: userId,
        name: cachedName || `User ${userId.slice(0, 6)}`, // Fallback to partial ID
        is_typing: false,
      };
    };

    switch (message.message_type) {
      case ThreadSocketMessageType.USER_JOINED: {
        // Update viewers list from server
        // Server sends viewers as array of user IDs, we need to enrich with names
        const joinedViewers = message.viewers.map((userId) =>
          getViewerFromId(userId)
        );
        setViewers(joinedViewers);
        break;
      }

      case ThreadSocketMessageType.USER_LEFT:
        // Remove user from viewers
        if (message.user_id) {
          setViewers((prev) =>
            prev.filter((v) => v.user_id !== message.user_id)
          );
        }
        break;

      case ThreadSocketMessageType.USER_FOCUS:
        // User started typing - set is_typing = true
        if (message.user_id) {
          setViewers((prev) =>
            prev.map((v) =>
              v.user_id === message.user_id ? { ...v, is_typing: true } : v
            )
          );
        }
        break;

      case ThreadSocketMessageType.USER_BLUR:
        // User stopped typing - set is_typing = false
        if (message.user_id) {
          setViewers((prev) =>
            prev.map((v) =>
              v.user_id === message.user_id ? { ...v, is_typing: false } : v
            )
          );
        }
        break;

      case ThreadSocketMessageType.MESSAGE_CREATED:
      case ThreadSocketMessageType.MESSAGE_UPDATED:
      case ThreadSocketMessageType.MESSAGE_DELETED:
        // Message changed - trigger refetch
        onMessageUpdate?.();

        // Auto-mark as read if user is actively viewing the thread
        if (
          message.message_type === ThreadSocketMessageType.MESSAGE_CREATED &&
          isPageVisible
        ) {
          send({
            message_type: ThreadSocketMessageType.MARK_READ,
          } as ClientMessage);
        }
        break;

      default:
        console.log(
          '[useThreadConnection] Unknown message type:',
          message.message_type
        );
    }
  }, [lastMessage, userNameCache, onMessageUpdate, isPageVisible, send]);

  // Handle input focus (user started typing)
  const handleInputFocus = useCallback(() => {
    send({ message_type: ThreadSocketMessageType.USER_FOCUS } as ClientMessage);
  }, [send]);

  // Handle input blur (user stopped typing)
  const handleInputBlur = useCallback(() => {
    send({ message_type: ThreadSocketMessageType.USER_BLUR } as ClientMessage);
  }, [send]);

  // Mark thread as read
  const sendMarkRead = useCallback(() => {
    send({ message_type: ThreadSocketMessageType.MARK_READ } as ClientMessage);
  }, [send]);

  return {
    viewers,
    isConnected,
    handleInputFocus,
    handleInputBlur,
    sendMarkRead,
    // Expose user cache setter for updating names when user data is loaded
    updateUserName: useCallback((userId: string, name: string) => {
      setUserNameCache((prev) => new Map(prev).set(userId, name));
    }, []),
  };
}
