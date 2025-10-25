'use client';

import { useState } from 'react';
import type {
  MessageSchema,
  MessageSchemaContent,
} from '@/openapi/managerLab.schemas';
import { MessageAvatar } from './message-avatar';
import { MessageContent } from './message-content';
import { MessageInput } from './message-input';
import { MessageActions } from './message-actions';
import { formatRelativeTime, validateMessageContent } from './message-utils';

interface MessageItemProps {
  message: MessageSchema;
  isCurrentUser: boolean;
  onEdit?: (messageId: string, content: MessageSchemaContent) => Promise<void>;
  onDelete?: (messageId: string) => Promise<void>;
}

export function MessageItem({
  message,
  isCurrentUser,
  onEdit,
  onDelete,
}: MessageItemProps) {
  const [isEditing, setIsEditing] = useState(false);

  const handleSaveEdit = async (content: MessageSchemaContent) => {
    if (
      !onEdit ||
      !validateMessageContent(content) ||
      JSON.stringify(content) === JSON.stringify(message.content)
    ) {
      setIsEditing(false);
      return;
    }

    await onEdit(message.id as string, content);
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (!onDelete) return;

    const confirmed = window.confirm(
      'Are you sure you want to delete this message?'
    );
    if (!confirmed) return;

    try {
      await onDelete(message.id as string);
    } catch (error) {
      console.error('Failed to delete message:', error);
    }
  };

  const wasEdited = message.updated_at !== message.created_at;

  return (
    <div className="hover:bg-muted/50 group flex gap-3 px-4 py-3">
      <MessageAvatar userName={message.user.name} />

      <div className="flex-1 space-y-1">
        <div className="flex items-baseline gap-2">
          <span className="text-sm font-semibold">{message.user.name}</span>
          <span className="text-muted-foreground text-xs">
            {formatRelativeTime(message.created_at)}
          </span>
          {wasEdited && (
            <span className="text-muted-foreground text-xs italic">
              (edited)
            </span>
          )}
        </div>

        {isEditing ? (
          <MessageInput
            mode="edit"
            initialContent={message.content}
            onSendMessage={handleSaveEdit}
            onCancel={handleCancelEdit}
          />
        ) : (
          <MessageContent
            content={message.content}
            className="text-foreground/90"
          />
        )}
      </div>

      {isCurrentUser && !isEditing && (
        <MessageActions
          onEdit={() => setIsEditing(true)}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}
