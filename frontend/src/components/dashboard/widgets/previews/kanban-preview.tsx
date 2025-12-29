import { Columns3 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface KanbanPreviewProps {
  className?: string;
}

export function KanbanPreview({ className }: KanbanPreviewProps) {
  return (
    <div
      className={cn(
        'flex h-12 w-full items-center justify-center gap-2',
        className
      )}
    >
      <Columns3 className="text-muted-foreground h-6 w-6" />
      <div className="flex gap-1">
        <div className="h-8 w-2 rounded-sm bg-blue-500/20" />
        <div className="h-8 w-2 rounded-sm bg-yellow-500/20" />
        <div className="h-8 w-2 rounded-sm bg-green-500/20" />
      </div>
    </div>
  );
}
