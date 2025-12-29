import { useThreadConnection } from './useThreadConnection';
import { useThreadMessages } from './useThreadMessages';
import { ObjectTypes, UserSchema } from '@/openapi/ariveAPI.schemas';

interface UseThreadSyncOptions {
  threadableType: ObjectTypes;
  threadableId: string;
  enabled?: boolean;
  currentUserId: string;
  user: UserSchema;
}

/**
 * Combines thread connection (WebSocket) and message management
 * into a single hook for easy consumption.
 */
export function useThreadSync({
  threadableType,
  threadableId,
  enabled = true,
  currentUserId,
  user,
}: UseThreadSyncOptions) {
  // Message management
  const {
    messages,
    isLoading,
    isSending,
    sendMessage,
    editMessage,
    deleteMessage,
    refetchMessages,
  } = useThreadMessages({
    threadableType,
    threadableId,
    enabled,
    user,
  });

  // WebSocket connection
  const {
    viewers,
    isConnected,
    handleInputFocus,
    handleInputBlur,
    sendMarkRead,
    updateUserName,
  } = useThreadConnection({
    threadableType,
    threadableId,
    enabled,
    onMessageUpdate: refetchMessages,
  });

  // Get typing users (excluding current user)
  const typingUsers = viewers.filter(
    (v) => v.is_typing && v.user_id !== currentUserId
  );

  // Get active viewers (excluding current user)
  const activeViewers = viewers.filter((v) => v.user_id !== currentUserId);

  return {
    // Messages
    messages,
    isLoading,
    isSending,
    sendMessage,
    editMessage,
    deleteMessage,
    refetchMessages,
    // Connection
    viewers,
    activeViewers,
    typingUsers,
    isConnected,
    handleInputFocus,
    handleInputBlur,
    sendMarkRead,
    updateUserName,
  };
}
