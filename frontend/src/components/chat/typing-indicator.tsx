'use client';

import { Avatar, AvatarFallback } from '@/components/ui/avatar';

interface TypingUser {
  user_id: string;
  name: string;
  is_typing: boolean;
}

interface TypingIndicatorProps {
  typingUsers: TypingUser[];
}

function getUserInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function TypingIndicator({ typingUsers }: TypingIndicatorProps) {
  if (typingUsers.length === 0) return null;

  const names = typingUsers.map((u) => u.name);
  const displayText =
    names.length === 1
      ? `${names[0]} is typing...`
      : names.length === 2
        ? `${names[0]} and ${names[1]} are typing...`
        : `${names[0]} and ${names.length - 1} others are typing...`;

  return (
    <div className="text-muted-foreground flex items-center gap-2 px-4 py-2 text-sm">
      <div className="flex -space-x-2">
        {typingUsers.slice(0, 3).map((user) => (
          <Avatar
            key={user.user_id}
            className="border-background h-6 w-6 border-2"
          >
            <AvatarFallback className="text-xs">
              {getUserInitials(user.name)}
            </AvatarFallback>
          </Avatar>
        ))}
      </div>
      <span className="italic">{displayText}</span>
      <span className="flex gap-1">
        <span className="animate-bounce" style={{ animationDelay: '0ms' }}>
          .
        </span>
        <span className="animate-bounce" style={{ animationDelay: '150ms' }}>
          .
        </span>
        <span className="animate-bounce" style={{ animationDelay: '300ms' }}>
          .
        </span>
      </span>
    </div>
  );
}
