'use client';

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { Badge } from '@/components/ui/badge';
import { ActivityFeedList } from '@/components/activity/activity-feed-list';
import { MessageInput } from '@/components/chat/message-input';
import { TypingIndicator } from '@/components/chat/typing-indicator';
import { useThreadSync } from '@/hooks/useThreadSync';
import { ObjectTypes } from '@/openapi/managerLab.schemas';
import type { DeliverableMediaAssociationSchema } from '@/openapi/managerLab.schemas';
import { cn } from '@/lib/utils';

interface MediaThreadCardProps {
  mediaAssociation: DeliverableMediaAssociationSchema;
  mediaIndex: number;
  currentUserId: string;
  defaultOpen?: boolean;
}

export function MediaThreadCard({
  mediaAssociation,
  mediaIndex,
  currentUserId,
  defaultOpen = false,
}: MediaThreadCardProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const {
    messages,
    isLoading,
    isSending,
    sendMessage,
    editMessage,
    deleteMessage,
    typingUsers,
    handleInputFocus,
    handleInputBlur,
  } = useThreadSync({
    threadableType: ObjectTypes.media,
    threadableId: String(mediaAssociation.media.id),
    currentUserId,
    enabled: true,
  });

  // Get last message for preview
  const lastMessage = messages[messages.length - 1];
  const lastMessagePreview = lastMessage
    ? typeof lastMessage.content === 'string'
      ? lastMessage.content
      : JSON.stringify(lastMessage.content)
    : 'No comments yet';

  // TODO: Get unread count from thread data
  const unreadCount = 0;

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <Card>
        <CollapsibleTrigger asChild>
          <CardHeader className="hover:bg-accent cursor-pointer transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CardTitle className="text-sm font-medium">
                  Frame {mediaIndex} Comments
                </CardTitle>
                {unreadCount > 0 && (
                  <Badge variant="default" className="text-xs">
                    {unreadCount}
                  </Badge>
                )}
              </div>
              <ChevronDown
                className={cn(
                  'h-4 w-4 transition-transform duration-200',
                  isOpen && 'rotate-180'
                )}
              />
            </div>
            {!isOpen && (
              <p className="text-muted-foreground mt-1 truncate text-xs">
                {lastMessagePreview}
              </p>
            )}
          </CardHeader>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className="space-y-4 pt-0">
            {/* Messages list - scrollable */}
            <div className="max-h-[300px] overflow-y-auto rounded-lg border">
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
              <TypingIndicator typingUsers={typingUsers} />
            )}

            {/* Message input */}
            <div className="rounded-lg border">
              <MessageInput
                onSendMessage={sendMessage}
                onFocus={handleInputFocus}
                onBlur={handleInputBlur}
                disabled={isSending}
              />
            </div>
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );
}
