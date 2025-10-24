'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { Users } from 'lucide-react';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { MessageList } from './chat/message-list';
import { MessageInput } from './chat/message-input';
import { TypingIndicator } from './chat/typing-indicator';
import {
  useThreadsThreadableTypeThreadableIdMessagesListMessages,
  useThreadsThreadableTypeThreadableIdMessagesCreateMessage,
  useThreadsThreadableTypeThreadableIdMarkReadMarkThreadRead,
} from '@/openapi/threads/threads';

interface ChatDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  threadableType: string;
  threadableId: number;
  currentUserId: string;
  title?: string;
}

interface Viewer {
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

function getUserInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function ChatDrawer({
  open,
  onOpenChange,
  threadableType,
  threadableId,
  currentUserId,
  title = 'Chat',
}: ChatDrawerProps) {
  const wsRef = useRef<WebSocket | null>(null);
  const [viewers, setViewers] = useState<Viewer[]>([]);

  // Fetch messages
  const {
    data: messagesData,
    refetch: refetchMessages,
    isLoading,
  } = useThreadsThreadableTypeThreadableIdMessagesListMessages(
    threadableType,
    threadableId,
    { limit: 100, offset: 0 },
    {
      query: {
        enabled: open,
      },
    }
  );

  // Create message mutation
  const createMessageMutation =
    useThreadsThreadableTypeThreadableIdMessagesCreateMessage();

  // Mark as read mutation
  const markAsReadMutation =
    useThreadsThreadableTypeThreadableIdMarkReadMarkThreadRead();

  const messages = messagesData?.messages || [];

  // WebSocket connection
  useEffect(() => {
    if (!open) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/threads/${threadableType}/${threadableId}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
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
          // Refetch messages from REST API
          refetchMessages();
          break;

        case 'pong':
          // Handle pong response
          break;

        default:
          console.log('Unknown notification type:', notification.type);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
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
  }, [open, threadableType, threadableId, refetchMessages]);

  // Mark as read when drawer opens
  useEffect(() => {
    if (open && messages.length > 0) {
      markAsReadMutation.mutate({
        threadableType,
        threadableId,
        params: {
          user_id: parseInt(currentUserId, 10),
        },
      });
    }
  }, [
    open,
    messages.length,
    threadableType,
    threadableId,
    currentUserId,
    markAsReadMutation,
  ]);

  const handleSendMessage = async (content: string) => {
    await createMessageMutation.mutateAsync({
      threadableType,
      threadableId,
      data: { content },
      params: {
        user_id: parseInt(currentUserId, 10),
      },
    });
  };

  const handleTypingChange = useCallback((isTyping: boolean) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({ type: 'typing', is_typing: isTyping })
      );
    }
  }, []);

  const handleEditMessage = async (messageId: string, content: string) => {
    // Use the actions framework to edit messages
    const response = await fetch(`/actions/message_actions/${messageId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'message_actions__update',
        data: { content },
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to edit message');
    }

    await refetchMessages();
  };

  const handleDeleteMessage = async (messageId: string) => {
    // Use the actions framework to delete messages
    const response = await fetch(`/actions/message_actions/${messageId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'message_actions__delete',
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to delete message');
    }

    await refetchMessages();
  };

  // Get typing users (excluding current user)
  const typingUsers = viewers.filter(
    (v) => v.is_typing && v.user_id !== currentUserId
  );

  // Get active viewers (excluding current user)
  const activeViewers = viewers.filter((v) => v.user_id !== currentUserId);

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="flex w-[400px] flex-col p-0 sm:max-w-md"
      >
        <SheetHeader className="px-6 py-4">
          <SheetTitle>{title}</SheetTitle>
          {activeViewers.length > 0 && (
            <div className="text-muted-foreground flex items-center gap-2 pt-2 text-sm">
              <Users className="h-4 w-4" />
              <span>{activeViewers.length + 1} viewing</span>
              <div className="ml-2 flex -space-x-2">
                {activeViewers.slice(0, 5).map((viewer) => (
                  <Avatar
                    key={viewer.user_id}
                    className="border-background h-6 w-6 border-2"
                  >
                    <AvatarFallback className="text-xs">
                      {getUserInitials(viewer.name)}
                    </AvatarFallback>
                  </Avatar>
                ))}
              </div>
            </div>
          )}
        </SheetHeader>

        <Separator />

        <div className="flex flex-1 flex-col overflow-hidden">
          <MessageList
            messages={messages}
            currentUserId={currentUserId}
            isLoading={isLoading}
            onEditMessage={handleEditMessage}
            onDeleteMessage={handleDeleteMessage}
          />

          {typingUsers.length > 0 && (
            <>
              <Separator />
              <TypingIndicator typingUsers={typingUsers} />
            </>
          )}
        </div>

        <MessageInput
          onSendMessage={handleSendMessage}
          onTypingChange={handleTypingChange}
          disabled={createMessageMutation.isPending}
        />
      </SheetContent>
    </Sheet>
  );
}
