'use client';

import { useQueryClient } from '@tanstack/react-query';
import {
  useThreadsThreadableTypeThreadableIdMessagesListMessages,
  useThreadsThreadableTypeThreadableIdMessagesCreateMessage,
  getThreadsThreadableTypeThreadableIdMessagesListMessagesQueryKey,
} from '@/openapi/threads/threads';
import {
  ObjectTypes,
  MessageSchemaContent,
  MessageSchema,
  UserSchema,
  MessageListResponse,
} from '@/openapi/managerLab.schemas';

interface UseThreadMessagesOptions {
  threadableType: ObjectTypes;
  threadableId: string;
  enabled?: boolean;
  user: UserSchema;
}

export function useThreadMessages({
  threadableType,
  threadableId,
  enabled = true,
  user,
}: UseThreadMessagesOptions) {
  const queryClient = useQueryClient();

  // Get the query key for the messages list
  const queryKey =
    getThreadsThreadableTypeThreadableIdMessagesListMessagesQueryKey(
      threadableType,
      threadableId,
      { limit: 100, offset: 0 }
    );

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

  // Create message mutation with optimistic updates
  const createMessageMutation =
    useThreadsThreadableTypeThreadableIdMessagesCreateMessage({
      mutation: {
        onMutate: async (variables) => {
          // Cancel any outgoing refetches to avoid overwriting optimistic update
          await queryClient.cancelQueries({ queryKey });

          // Snapshot the previous value
          const previousMessages =
            queryClient.getQueryData<MessageListResponse>(queryKey);

          // Optimistically update the cache
          if (previousMessages) {
            // Create optimistic message with temporary ID
            // The 'as unknown as MessageSchema' cast is needed because we're using
            // a temporary string ID that will be replaced by the server response
            const optimisticMessage = {
              id: `optimistic-${Date.now()}`,
              thread_id: '', // Will be filled by server
              user_id: user.id,
              content: variables.data.content,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              user: {
                id: user.id,
                email: user.email,
                name: user.name,
              },
            } as unknown as MessageSchema;

            queryClient.setQueryData<MessageListResponse>(queryKey, {
              ...previousMessages,
              messages: [...previousMessages.messages, optimisticMessage],
            });
          }

          // Return context with snapshot for rollback
          return { previousMessages };
        },
        onError: (err, variables, context) => {
          // Rollback on error
          if (context?.previousMessages) {
            queryClient.setQueryData(queryKey, context.previousMessages);
          }
        },
        onSettled: () => {
          // Always refetch after mutation to sync with server
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
