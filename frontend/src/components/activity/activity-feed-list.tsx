'use client';

import { Loader2 } from 'lucide-react';
import { ActivityFeedItem } from './activity-feed-item';
import type {
  MessageSchema,
  MessageSchemaContent,
} from '@/openapi/ariveAPI.schemas';

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
    <div className="space-y-0 p-4">
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
    </div>
  );
}
