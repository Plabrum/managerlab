'use client';

import {
  useThreadsThreadableTypeThreadableIdMessagesListMessages,
  useThreadsThreadableTypeThreadableIdMessagesCreateMessage,
} from '@/openapi/threads/threads';
import {
  ObjectTypes,
  MessageSchemaContent,
} from '@/openapi/managerLab.schemas';

interface UseThreadMessagesOptions {
  threadableType: ObjectTypes;
  threadableId: string;
  enabled?: boolean;
}

export function useThreadMessages({
  threadableType,
  threadableId,
  enabled = true,
}: UseThreadMessagesOptions) {
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
        enabled,
      },
    }
  );

  // Create message mutation
  const createMessageMutation =
    useThreadsThreadableTypeThreadableIdMessagesCreateMessage({
      mutation: {
        onSuccess: () => {
          // Immediately refetch messages to show the new message
          refetchMessages();
        },
      },
    });

  const messages = messagesData?.messages || [];

  // Send message
  const sendMessage = async (content: MessageSchemaContent) => {
    await createMessageMutation.mutateAsync({
      threadableType,
      threadableId,
      data: { content },
    });
  };

  // Edit message
  const editMessage = async (
    messageId: string,
    content: MessageSchemaContent
  ) => {
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

  // Delete message
  const deleteMessage = async (messageId: string) => {
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

  return {
    messages,
    isLoading,
    isSending: createMessageMutation.isPending,
    sendMessage,
    editMessage,
    deleteMessage,
    refetchMessages,
  };
}
