'use client';

import { useEffect, useRef } from 'react';
import { ActivityFeedList } from './activity-feed-list';
import { MessageInput } from '@/components/chat/message-input';
import { TypingIndicator } from '@/components/chat/typing-indicator';
import { ThreadViewers } from '@/components/chat/thread-viewers';
import { useThreadSync } from '@/hooks/useThreadSync';
import { useAuth } from '@/components/providers/auth-provider';
import { ObjectTypes } from '@/openapi/ariveAPI.schemas';

interface ActivityFeedProps {
  threadableType: ObjectTypes;
  threadableId: string;
  currentUserId: string;
  showViewers?: boolean;
}

/**
 * ActivityFeed displays a thread's messages in an inline layout
 * (as opposed to ChatDrawer which uses a Sheet/drawer).
 *
 * This component is designed to be used in tabs on detail pages
 * and can be extended in the future to show other activity types
 * beyond just messages (field changes, state transitions, etc.)
 */
export function ActivityFeed({
  threadableType,
  threadableId,
  currentUserId,
  showViewers = true,
}: ActivityFeedProps) {
  const { currentTeamId, user } = useAuth();
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const prevMessagesLengthRef = useRef(0);

  // Only enable WebSocket connection when a team scope is set
  // This prevents authentication errors when the session doesn't have a scope yet
  const enabled = currentTeamId !== null;

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

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (
      messages.length > prevMessagesLengthRef.current &&
      scrollContainerRef.current
    ) {
      // Use requestAnimationFrame to ensure DOM has updated before scrolling
      requestAnimationFrame(() => {
        if (scrollContainerRef.current) {
          scrollContainerRef.current.scrollTo({
            top: scrollContainerRef.current.scrollHeight,
            behavior: 'smooth',
          });
        }
      });
    }
    prevMessagesLengthRef.current = messages.length;
  }, [messages.length]);

  return (
    <div className="flex max-h-full flex-col">
      {/* Header with viewers */}
      {showViewers && activeViewers.length > 0 && (
        <div className="mb-4">
          <ThreadViewers viewers={activeViewers} />
        </div>
      )}

      {/* Activity feed - flex to fill available space with internal scroll */}
      <div
        ref={scrollContainerRef}
        className="max-h-[60vh] min-h-0 flex-1 overflow-y-auto rounded-lg "
      >
        <ActivityFeedList
          messages={messages}
          currentUserId={currentUserId}
          isLoading={isLoading}
          onEditMessage={editMessage}
          onDeleteMessage={deleteMessage}
        />
      </div>

      {/* Typing indicator */}
      {typingUsers.length > 0 && (
        <div className="mt-2">
          <TypingIndicator typingUsers={typingUsers} />
        </div>
      )}

      {/* Message input - fixed at bottom */}
      <div className="mt-4 rounded-lg border">
        <MessageInput
          onSendMessage={sendMessage}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          disabled={isSending}
        />
      </div>
    </div>
  );
}
