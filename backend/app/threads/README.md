# Threads API - Frontend Integration Guide

## Overview

The threads system provides real-time messaging for any object in the platform. Any entity (DeliverableMedia, Campaign, Invoice, etc.) can have a single thread with multiple messages.

**Key Features:**
- REST API for creating messages and listing threads
- Actions framework for update/delete with automatic permission checking
- WebSocket for real-time updates
- Unread message tracking per user
- Soft deletes for message history

## Authentication

All endpoints require authentication via the `requires_user_scope` guard. Ensure your requests include valid session credentials.

## REST API Endpoints

All endpoints are prefixed with `/threads`

### 1. Create Message

**POST** `/threads/{threadable_type}/{threadable_id}/messages`

Creates a new message in a thread. Auto-creates the thread if it doesn't exist.

**Parameters:**
- `threadable_type` (path): Object type, e.g., "DeliverableMedia", "Campaign"
- `threadable_id` (path): Object ID

**Request Body:**
```json
{
  "content": "Your message here"
}
```

**Response:**
```json
{
  "id": "abc123",
  "thread_id": 1,
  "user_id": 42,
  "content": "Your message here",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "user": {
    "id": "user123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### 2. List Messages

**GET** `/threads/{threadable_type}/{threadable_id}/messages?offset=0&limit=50`

Retrieves paginated messages, most recent first. Returns empty list if thread doesn't exist.

**Query Parameters:**
- `offset` (optional): Pagination offset, default 0
- `limit` (optional): Number of messages (1-100), default 50

**Response:**
```json
{
  "messages": [
    {
      "id": "abc123",
      "thread_id": "thread456",
      "user_id": "user789",
      "content": "Message content",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z",
      "user": {
        "id": "user789",
        "email": "user@example.com",
        "name": "John Doe"
      }
    }
  ],
  "offset": 0,
  "limit": 50
}
```

### 3. Get Batch Unread Counts

**POST** `/threads/{threadable_type}/batch-unread`

Get unread counts for multiple objects in a single request. This is much more efficient than calling a single unread endpoint multiple times when displaying a list of objects (e.g., list of deliverables with unread badges).

**Request Body:**
```json
{
  "object_ids": [123, 456, 789]
}
```

**Response:**
```json
{
  "threads": [
    {
      "threadable_id": 123,
      "thread_id": "abc123",
      "unread_count": 5
    },
    {
      "threadable_id": 456,
      "thread_id": "def456",
      "unread_count": 0
    },
    {
      "threadable_id": 789,
      "thread_id": null,
      "unread_count": 0
    }
  ],
  "total_unread": 5
}
```

**Notes:**
- Returns an entry for every requested `object_id`, even if no thread exists (thread_id will be null)
- `total_unread` is the sum of all unread counts across all threads
- Single efficient database query regardless of how many object_ids are requested

### 4. Mark Thread as Read

**POST** `/threads/{threadable_type}/{threadable_id}/mark-read`

Marks all messages in the thread as read for the current user.

**Response:** 204 No Content

## Message Actions (Update/Delete)

Message update and delete operations use the platform's actions framework for consistent permission handling.

### List Available Actions for a Message

**GET** `/actions/message_actions/{message_id}`

Returns available actions for the given message. Only returns actions the current user can perform (e.g., only message author sees "Edit" and "Delete").

**Response:**
```json
{
  "actions": [
    {
      "action": "message_actions__update",
      "label": "Edit",
      "is_bulk_allowed": false,
      "priority": 10,
      "icon": "edit",
      "confirmation_message": null,
      "should_redirect_to_parent": false
    },
    {
      "action": "message_actions__delete",
      "label": "Delete",
      "is_bulk_allowed": false,
      "priority": 20,
      "icon": "trash",
      "confirmation_message": "Are you sure you want to delete this message?",
      "should_redirect_to_parent": true
    }
  ]
}
```

### Execute Message Action

**POST** `/actions/message_actions/{message_id}`

Execute an action on a message using a discriminated union payload.

#### Update Message

**Request Body:**
```json
{
  "action": "message_actions__update",
  "data": {
    "content": "Updated message content"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Updated message",
  "results": {},
  "should_redirect_to_parent": false
}
```

#### Delete Message

**Request Body:**
```json
{
  "action": "message_actions__delete"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Deleted message",
  "results": {},
  "should_redirect_to_parent": true
}
```

**Notes:**
- Actions automatically check permissions (only message author can edit/delete)
- Attempting an unauthorized action returns a 403 Forbidden
- Both operations trigger WebSocket notifications (`message_updated` / `message_deleted`)
- Delete performs a soft-delete (sets `deleted_at` timestamp)

## WebSocket - Real-Time Updates

### Connection

**URL:** `ws://your-domain/ws/threads/{threadable_type}/{threadable_id}`

The WebSocket connection provides real-time notifications when messages are created, updated, or deleted.

### Connection Flow

1. **Connect** to the WebSocket URL
2. **Server verifies** thread access via RLS
3. **Server subscribes** to PostgreSQL notifications for this thread
4. **Receive notifications** as JSON messages

### Notification Types

**New Message:**
```json
{
  "type": "new_message",
  "thread_id": 1,
  "user_id": 42
}
```

**Message Updated:**
```json
{
  "type": "message_updated",
  "message_id": 123
}
```

**Message Deleted:**
```json
{
  "type": "message_deleted",
  "message_id": 123
}
```

**Note:** Notification payloads contain internal IDs for metadata purposes only. The frontend should not use these IDs directly - always re-fetch data via REST API after receiving a notification to get properly formatted responses with sqids.

### Keepalive (Optional)

Send ping messages to keep connection alive:

**Send:**
```json
{
  "type": "ping",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Receive:**
```json
{
  "type": "pong",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Typical Workflow

### Displaying a Thread

1. **Fetch initial messages**: `GET /threads/{type}/{id}/messages`
2. **Connect WebSocket**: `ws://.../ws/threads/{type}/{id}`
3. **On notification received**: Query REST API for updated data
4. **Mark as read**: `POST /threads/{type}/{id}/mark-read` when user views thread

### Creating a Message

1. **Send message**: `POST /threads/{type}/{id}/messages`
2. **All connected clients** receive WebSocket notification
3. **Clients fetch updated messages** via REST API

### Editing/Deleting a Message

1. **Check available actions**: `GET /actions/message_actions/{message_id}` (optional - for showing UI)
2. **Execute action**: `POST /actions/message_actions/{message_id}` with action payload
3. **All connected clients** receive WebSocket notification
4. **Clients fetch updated messages** via REST API

### Unread Badges (List View)

1. **Get batch unread counts**: `POST /threads/{type}/batch-unread` with list of object IDs
2. **Display badges** for each object with unread count > 0
3. **Listen for notifications** via WebSocket (optional - for real-time updates)
4. **Refresh badges** when notification received
5. **Clear badge**: `POST /threads/{type}/{id}/mark-read` when user opens thread

**Example for list of 50 deliverables:**
- Old way: 50 individual GET requests
- New way: 1 POST request with all 50 IDs

## Important Notes

### RLS (Row-Level Security)
- All queries are automatically scoped by `team_id` and `campaign_id` from session
- Users can only access threads for objects they have permission to view
- WebSocket connections are automatically closed if thread access is denied

### Soft Deletes
- Deleted messages have `deleted_at` timestamp set
- Deleted messages are excluded from list queries
- Message counts exclude soft-deleted messages

### Thread Auto-Creation
- Threads are created automatically when the first message is posted
- No need to explicitly create a thread before posting

### Message IDs
- All public IDs use SQID encoding
- Internal database IDs are never exposed to the frontend

## Example: React Integration

```typescript
import { useState, useEffect } from 'react';

function ThreadView({ threadableType, threadableId }) {
  const [messages, setMessages] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    // Fetch initial messages
    fetch(`/threads/${threadableType}/${threadableId}/messages`)
      .then(res => res.json())
      .then(data => setMessages(data.messages));

    // Connect WebSocket
    const socket = new WebSocket(
      `ws://localhost:8000/ws/threads/${threadableType}/${threadableId}`
    );

    socket.onmessage = (event) => {
      const notification = JSON.parse(event.data);

      if (['new_message', 'message_updated', 'message_deleted'].includes(notification.type)) {
        // Re-fetch messages for any change
        fetch(`/threads/${threadableType}/${threadableId}/messages`)
          .then(res => res.json())
          .then(data => setMessages(data.messages));
      }
    };

    setWs(socket);

    return () => socket.close();
  }, [threadableType, threadableId]);

  const sendMessage = async (content) => {
    await fetch(`/threads/${threadableType}/${threadableId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });
    // WebSocket notification will trigger re-fetch
  };

  const editMessage = async (messageId, newContent) => {
    await fetch(`/actions/message_actions/${messageId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'message_actions__update',
        data: { content: newContent }
      })
    });
    // WebSocket notification will trigger re-fetch
  };

  const deleteMessage = async (messageId) => {
    const confirmed = window.confirm('Are you sure you want to delete this message?');
    if (!confirmed) return;

    await fetch(`/actions/message_actions/${messageId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'message_actions__delete'
      })
    });
    // WebSocket notification will trigger re-fetch
  };

  const markAsRead = async () => {
    await fetch(`/threads/${threadableType}/${threadableId}/mark-read`, {
      method: 'POST'
    });
  };

  return (
    <div>
      {/* Render messages with edit/delete buttons */}
      <button onClick={() => sendMessage('Hello!')}>Send</button>
      <button onClick={() => editMessage('msg123', 'Updated!')}>Edit</button>
      <button onClick={() => deleteMessage('msg123')}>Delete</button>
      <button onClick={markAsRead}>Mark as Read</button>
    </div>
  );
}
```

## Error Handling

- **404 Not Found**: Thread or message doesn't exist
- **403 Permission Denied**: User doesn't have access or trying to edit/delete someone else's message
- **1008 WebSocket Close**: Thread not found or access denied

## Performance Considerations

- WebSocket notifications are lightweight (metadata only)
- Always query REST API after receiving notification (don't send full message via WS)
- Use pagination for threads with many messages
- Mark threads as read when user views them to keep unread counts accurate
