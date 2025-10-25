'use client';

import { useState, useRef, useEffect } from 'react';
import { MinimalTiptap } from '@/components/ui/minimal-tiptap';
import type { MessageSchemaContent } from '@/openapi/managerLab.schemas';

interface MessageInputProps {
  onSendMessage: (content: MessageSchemaContent) => Promise<void>;
  onTypingChange?: (isTyping: boolean) => void;
  disabled?: boolean;
  // Edit mode props
  mode?: 'new' | 'edit';
  initialContent?: MessageSchemaContent;
  onCancel?: () => void;
}

interface TiptapNode {
  type?: string;
  content?: Array<{ text?: string }>;
}

interface TiptapContent {
  type?: string;
  content?: TiptapNode[];
}

/**
 * Checks if the content has any non-empty text
 */
function hasContentText(content: MessageSchemaContent | null): boolean {
  if (!content || typeof content !== 'object') {
    return false;
  }

  // Type guard for TipTap content structure
  const hasContentArray =
    'content' in content && Array.isArray(content.content);
  if (!hasContentArray) {
    return false;
  }

  const tiptapContent = content as TiptapContent;
  return (tiptapContent.content ?? []).some((node: TiptapNode) =>
    Array.isArray(node.content)
      ? node.content.some((child) => child.text && child.text.trim())
      : false
  );
}

export function MessageInput({
  onSendMessage,
  onTypingChange,
  disabled = false,
  mode = 'new',
  initialContent,
  onCancel,
}: MessageInputProps) {
  const [content, setContent] = useState<MessageSchemaContent | null>(
    initialContent || null
  );
  const [isSending, setIsSending] = useState(false);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const isEditMode = mode === 'edit';

  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  const handleContentChange = (value: MessageSchemaContent) => {
    setContent(value);

    // Send typing indicator (only in new message mode)
    if (!isEditMode && onTypingChange) {
      if (hasContentText(value)) {
        onTypingChange(true);

        // Clear existing timeout
        if (typingTimeoutRef.current) {
          clearTimeout(typingTimeoutRef.current);
        }

        // Auto-clear typing after 3 seconds of inactivity
        typingTimeoutRef.current = setTimeout(() => {
          onTypingChange(false);
        }, 3000);
      } else {
        onTypingChange(false);
      }
    }
  };

  const handleSend = async () => {
    if (!hasContentText(content) || isSending || disabled) return;

    setIsSending(true);
    try {
      await onSendMessage(content!);

      // Only clear content in new message mode
      if (!isEditMode) {
        setContent(null);
        if (onTypingChange) {
          onTypingChange(false);
        }

        // Clear typing timeout
        if (typingTimeoutRef.current) {
          clearTimeout(typingTimeoutRef.current);
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <MinimalTiptap
      content={content}
      onChange={handleContentChange}
      placeholder={isEditMode ? 'Edit message...' : 'Type a message...'}
      editable={!disabled && !isSending}
      editorClassName={isEditMode ? '' : 'min-h-20'}
      toolbar="minimal"
      onSend={handleSend}
      isSending={isSending}
      mode={mode}
      onCancel={onCancel}
    />
  );
}
