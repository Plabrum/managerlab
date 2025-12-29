import { MessageInput } from './chat/message-input';
import { MessageList } from './chat/message-list';
import { ThreadViewers } from './chat/thread-viewers';
import { TypingIndicator } from './chat/typing-indicator';
import { useAuth } from '@/components/providers/auth-provider';
import { Separator } from '@/components/ui/separator';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { useThreadSync } from '@/hooks/useThreadSync';
import { ObjectTypes } from '@/openapi/ariveAPI.schemas';

interface ChatDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  threadableType: ObjectTypes;
  threadableId: string;
  currentUserId: string;
  title?: string;
}

/**
 * ChatDrawer provides a drawer/sheet interface for threads.
 * Refactored to use shared hooks for thread management.
 *
 * This component is kept for future user-to-user chat functionality.
 * For object-based threads on detail pages, use ObjectDetailTabs with ActivityFeed instead.
 */
export function ChatDrawer({
  open,
  onOpenChange,
  threadableType,
  threadableId,
  currentUserId,
  title = 'Chat',
}: ChatDrawerProps) {
  const { currentTeamId, user } = useAuth();

  // Only enable WebSocket when drawer is open AND team scope is set
  const enabled = open && currentTeamId !== null;

  const {
    messages,
    isLoading,
    isSending,
    sendMessage,
    editMessage,
    deleteMessage,
    activeViewers,
    typingUsers,
    handleInputFocus,
    handleInputBlur,
  } = useThreadSync({
    threadableType,
    threadableId,
    currentUserId,
    user,
    enabled,
  });

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="flex w-[400px] flex-col p-0 sm:max-w-md"
      >
        <SheetHeader className="px-6 py-4">
          <SheetTitle>{title}</SheetTitle>
          {activeViewers.length > 0 && (
            <ThreadViewers viewers={activeViewers} className="pt-2" />
          )}
        </SheetHeader>

        <Separator />

        <div className="flex flex-1 flex-col overflow-hidden">
          <MessageList
            messages={messages}
            currentUserId={currentUserId}
            isLoading={isLoading}
            onEditMessage={editMessage}
            onDeleteMessage={deleteMessage}
          />

          {typingUsers.length > 0 && (
            <>
              <Separator />
              <TypingIndicator typingUsers={typingUsers} />
            </>
          )}
        </div>

        <MessageInput
          onSendMessage={sendMessage}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          disabled={isSending}
        />
      </SheetContent>
    </Sheet>
  );
}
