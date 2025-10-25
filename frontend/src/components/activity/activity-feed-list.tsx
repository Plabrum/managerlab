'use client';

import { useEffect, useRef } from 'react';
import { Loader2 } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ActivityFeedItem } from './activity-feed-item';
import type {
  MessageSchema,
  MessageSchemaContent,
} from '@/openapi/managerLab.schemas';

interface ActivityFeedListProps {
  messages: MessageSchema[];
  currentUserId: string;
  isLoading?: boolean;
  onEditMessage?: (
    messageId: string,
    content: MessageSchemaContent
  ) => Promise<void>;
  onDeleteMessage?: (messageId: string) => Promise<void>;
}

export function ActivityFeedList({
  messages,
  currentUserId,
  isLoading = false,
  onEditMessage,
  onDeleteMessage,
}: ActivityFeedListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const prevMessagesLengthRef = useRef(messages.length);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messages.length > prevMessagesLengthRef.current) {
      scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
    prevMessagesLengthRef.current = messages.length;
  }, [messages.length]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="text-muted-foreground h-6 w-6 animate-spin" />
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground text-sm">
          No activity yet. Start the conversation!
        </p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full flex-1 ">
      <div className="space-y-0 p-2">
        {messages.map((message, index) => (
          <ActivityFeedItem
            key={message.id as string}
            message={message}
            isCurrentUser={message.user_id === currentUserId}
            isLast={index === messages.length - 1}
            onEdit={onEditMessage}
            onDelete={onDeleteMessage}
          />
        ))}
        <div ref={scrollRef} />
      </div>
    </ScrollArea>
  );
}
