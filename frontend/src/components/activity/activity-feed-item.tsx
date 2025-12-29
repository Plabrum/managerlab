import { useState } from 'react';
import { toast } from 'sonner';
import { MessageActions } from '@/components/chat/message-actions';
import { MessageAvatar } from '@/components/chat/message-avatar';
import { MessageContent } from '@/components/chat/message-content';
import { MessageInput } from '@/components/chat/message-input';
import {
  formatRelativeTime,
  validateMessageContent,
} from '@/components/chat/message-utils';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import type {
  MessageSchema,
  MessageSchemaContent,
} from '@/openapi/ariveAPI.schemas';

interface ActivityFeedItemProps {
  message: MessageSchema;
  isCurrentUser: boolean;
  isLast: boolean;
  onEdit?: (messageId: string, content: MessageSchemaContent) => Promise<void>;
  onDelete?: (messageId: string) => Promise<void>;
}

export function ActivityFeedItem({
  message,
  isCurrentUser,
  isLast,
  onEdit,
  onDelete,
}: ActivityFeedItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const handleSaveEdit = async (content: MessageSchemaContent) => {
    if (
      !onEdit ||
      !validateMessageContent(content) ||
      JSON.stringify(content) === JSON.stringify(message.content)
    ) {
      setIsEditing(false);
      return;
    }

    try {
      await onEdit(String(message.id), content);
      setIsEditing(false);
      toast.success('Message updated successfully');
    } catch (error) {
      toast.error('Failed to update message');
      console.error('Failed to update message:', error);
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleDeleteClick = () => {
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    if (!onDelete) return;

    try {
      await onDelete(String(message.id));
      setShowDeleteDialog(false);
      toast.success('Message deleted successfully');
    } catch (error) {
      toast.error('Failed to delete message');
      console.error('Failed to delete message:', error);
    }
  };

  const wasEdited = message.updated_at !== message.created_at;

  return (
    <div className="group flex gap-2">
      {/* Timeline column with avatar and connecting line */}
      <div className="relative flex flex-col items-center">
        <MessageAvatar
          userName={message.user.name}
          className="bg-muted text-muted-foreground"
        />
        {!isLast && <div className="bg-border my-2 w-px flex-1" />}
      </div>

      {/* Content column */}
      <div className="flex-1">
        {/* Header with name, timestamp, and actions */}
        <div className="flex items-center gap-2">
          <span className="text-foreground text-sm font-medium">
            {message.user.name}
          </span>
          <span className="text-muted-foreground text-xs">
            {formatRelativeTime(message.created_at)}
          </span>
          {wasEdited && (
            <span className="text-muted-foreground text-xs italic">
              (edited)
            </span>
          )}
          {isCurrentUser && !isEditing && (
            <MessageActions
              onEdit={() => setIsEditing(true)}
              onDelete={handleDeleteClick}
              className="ml-auto"
            />
          )}
        </div>

        {/* Message content or editor */}
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
            className="text-foreground leading-relaxed"
          />
        )}
      </div>

      {/* Delete confirmation dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete message</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this message? This action cannot
              be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteConfirm}>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
