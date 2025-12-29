import { MessageCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface ChatButtonProps {
  unreadCount?: number;
  onClick: () => void;
}

export function ChatButton({ unreadCount = 0, onClick }: ChatButtonProps) {
  return (
    <div className="relative">
      <Button variant="outline" size="sm" onClick={onClick} className="gap-2">
        <MessageCircle className="h-4 w-4" />
        Chat
      </Button>
      {unreadCount > 0 && (
        <Badge
          variant="destructive"
          className="absolute -right-2 -top-2 h-5 min-w-5 px-1 text-xs"
        >
          {unreadCount > 99 ? '99+' : unreadCount}
        </Badge>
      )}
    </div>
  );
}
