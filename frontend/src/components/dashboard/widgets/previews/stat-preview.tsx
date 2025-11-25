'use client';

import { ArrowUpIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatPreviewProps {
  className?: string;
}

export function StatPreview({ className }: StatPreviewProps) {
  return (
    <div
      className={cn(
        'flex h-12 w-full items-center justify-center gap-2',
        className
      )}
    >
      <span className="text-xl font-bold">1,234</span>
      <div className="flex items-center gap-0.5 text-green-500">
        <ArrowUpIcon className="h-3 w-3" />
        <span className="text-xs font-medium">12%</span>
      </div>
    </div>
  );
}
