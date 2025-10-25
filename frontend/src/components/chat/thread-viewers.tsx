'use client';

import { Users } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

interface Viewer {
  user_id: string;
  name: string;
  is_typing: boolean;
}

interface ThreadViewersProps {
  viewers: Viewer[];
  maxAvatars?: number;
  className?: string;
}

function getUserInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function ThreadViewers({
  viewers,
  maxAvatars = 5,
  className = '',
}: ThreadViewersProps) {
  if (viewers.length === 0) return null;

  return (
    <div
      className={`text-muted-foreground flex items-center gap-2 text-sm ${className}`}
    >
      <Users className="h-4 w-4" />
      <span>{viewers.length + 1} viewing</span>
      <div className="ml-2 flex -space-x-2">
        {viewers.slice(0, maxAvatars).map((viewer) => (
          <Avatar
            key={viewer.user_id}
            className="border-background h-6 w-6 border-2"
          >
            <AvatarFallback className="text-xs">
              {getUserInitials(viewer.name)}
            </AvatarFallback>
          </Avatar>
        ))}
      </div>
    </div>
  );
}
