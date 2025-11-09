/**
 * Shared utilities for message components
 */

import type { MessageSchemaContent } from '@/openapi/ariveAPI.schemas';

interface TiptapNode {
  type?: string;
  content?: Array<{ text?: string }>;
}

interface TiptapContent {
  type?: string;
  content?: TiptapNode[];
}

/**
 * Format a date string as relative time (e.g., "2m ago", "3h ago")
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}

/**
 * Get user initials from a full name
 */
export function getUserInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

/**
 * Validate TipTap JSON content has actual text
 */
export function validateMessageContent(content: MessageSchemaContent): boolean {
  if (!content || typeof content !== 'object') return false;

  const tiptapContent = content as TiptapContent;
  const hasText =
    Array.isArray(tiptapContent.content) &&
    tiptapContent.content.some(
      (node: TiptapNode) =>
        Array.isArray(node.content) &&
        node.content.some((child) => child.text && child.text.trim())
    );

  return hasText;
}
