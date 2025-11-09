import { MinimalTiptap } from '@/components/ui/minimal-tiptap';
import { cn } from '@/lib/utils';
import type { MessageSchemaContent } from '@/openapi/ariveAPI.schemas';

interface MessageContentProps {
  content: MessageSchemaContent;
  className?: string;
}

export function MessageContent({ content, className }: MessageContentProps) {
  return (
    <div className={cn('text-sm', className)}>
      <MinimalTiptap
        content={content}
        editable={false}
        showToolbar={false}
        className="border-0"
      />
    </div>
  );
}
