/**
 * WebSocket message types and interfaces matching backend implementation.
 * Backend: app/threads/enums.py, app/threads/schemas.py
 */

/**
 * Message types for thread websocket communication.
 * Shared between client → server and server → client messages.
 */
export enum ThreadSocketMessageType {
  // Client → Server
  MARK_READ = 'mark_read', // User marked thread as read
  USER_FOCUS = 'user_focus', // User focused on thread input (started typing)
  USER_BLUR = 'user_blur', // User blurred from thread input (stopped typing)

  // Server → Client
  USER_JOINED = 'user_joined', // User joined thread
  USER_LEFT = 'user_left', // User left thread
  MESSAGE_CREATED = 'message_created', // New message created
  MESSAGE_UPDATED = 'message_updated', // Message updated
  MESSAGE_DELETED = 'message_deleted', // Message deleted
}

/**
 * Client → Server message structure.
 */
export interface ClientMessage {
  message_type: ThreadSocketMessageType;
}

/**
 * Server → Client message structure.
 * All messages include the current viewers list.
 */
export interface ServerMessage {
  message_type: ThreadSocketMessageType;
  viewers: string[]; // Array of Sqid-encoded user IDs currently viewing
  user_id?: string | null; // Sqid-encoded user ID (for presence/message events)
  message_id?: string | null; // Sqid-encoded message ID (for message events)
  thread_id?: string | null; // Sqid-encoded thread ID (for message events)
}

/**
 * Frontend viewer state (enriched with cached user data).
 */
export interface Viewer {
  user_id: string; // Sqid-encoded user ID
  name: string; // User name (cached from previous API calls)
  is_typing: boolean; // Typing state (managed by focus/blur events)
}
