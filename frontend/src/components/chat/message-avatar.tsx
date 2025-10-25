import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { getUserInitials } from './message-utils';
import { cn } from '@/lib/utils';

interface MessageAvatarProps {
  userName: string;
  className?: string;
}

export function MessageAvatar({ userName, className }: MessageAvatarProps) {
  return (
    <Avatar className={cn('h-8 w-8', className)}>
      <AvatarFallback className="text-xs">
        {getUserInitials(userName)}
      </AvatarFallback>
    </Avatar>
  );
}
