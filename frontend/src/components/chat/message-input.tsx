import { useState } from 'react';
import { MinimalTiptap } from '@/components/ui/minimal-tiptap';
import type { MessageSchemaContent } from '@/openapi/ariveAPI.schemas';

interface MessageInputProps {
  onSendMessage: (content: MessageSchemaContent) => Promise<void>;
  onFocus?: () => void;
  onBlur?: () => void;
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
  onFocus,
  onBlur,
  disabled = false,
  mode = 'new',
  initialContent,
  onCancel,
}: MessageInputProps) {
  const [content, setContent] = useState<MessageSchemaContent | null>(
    initialContent || null
  );
  const [isSending, setIsSending] = useState(false);

  const isEditMode = mode === 'edit';

  const handleContentChange = (value: MessageSchemaContent) => {
    setContent(value);
  };

  const handleSend = async () => {
    if (!hasContentText(content) || isSending || disabled) return;

    setIsSending(true);
    try {
      await onSendMessage(content!);

      // Only clear content in new message mode
      if (!isEditMode) {
        setContent(null);
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
      onFocus={onFocus}
      onBlur={onBlur}
    />
  );
}
