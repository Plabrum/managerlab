'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  Heart,
  MessageCircle,
  Send,
  Bookmark,
  MoreHorizontal,
} from 'lucide-react';
import { useState } from 'react';

interface InstagramPostProps {
  image_url: string;
  title: string;
  posting_date?: string;
  user_name: string;
  user_photo: string;
  user_handle: string;
}

export function InstagramPost({
  image_url,
  title,
  posting_date,
  user_name,
  user_photo,
  user_handle,
}: InstagramPostProps) {
  const [isLiked, setIsLiked] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  const formatDate = (date?: string) => {
    if (!date) return null;
    const postDate = new Date(date);
    const now = new Date();
    const diffInMs = now.getTime() - postDate.getTime();
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInHours / 24);
    const diffInWeeks = Math.floor(diffInDays / 7);

    if (diffInHours < 24) {
      return `${diffInHours}h`;
    } else if (diffInDays < 7) {
      return `${diffInDays}d`;
    } else if (diffInWeeks < 4) {
      return `${diffInWeeks}w`;
    } else {
      return postDate.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });
    }
  };

  return (
    <article className="border-border bg-card w-full max-w-[470px] border">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2.5">
        <div className="flex items-center gap-3">
          <Avatar className="h-8 w-8">
            <AvatarImage
              src={user_photo || '/placeholder.svg'}
              alt={user_name}
            />
            <AvatarFallback>{user_name.charAt(0).toUpperCase()}</AvatarFallback>
          </Avatar>
          <div className="flex flex-col">
            <span className="text-foreground text-sm font-semibold leading-tight">
              {user_handle}
            </span>
          </div>
        </div>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreHorizontal className="h-5 w-5" />
        </Button>
      </div>

      {/* Image */}
      <div className="bg-muted relative aspect-square w-full">
        <img
          src={image_url || '/placeholder.svg'}
          alt={title}
          className="h-full w-full object-cover"
        />
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between px-3 py-2">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setIsLiked(!isLiked)}
          >
            <Heart
              className={`h-6 w-6 ${isLiked ? 'fill-red-500 text-red-500' : ''}`}
            />
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <MessageCircle className="h-6 w-6" />
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <Send className="h-6 w-6" />
          </Button>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={() => setIsSaved(!isSaved)}
        >
          <Bookmark className={`h-6 w-6 ${isSaved ? 'fill-foreground' : ''}`} />
        </Button>
      </div>

      {/* Caption */}
      <div className="px-3 pb-3">
        <div className="mb-2">
          <span className="text-foreground text-sm font-semibold">
            {user_handle}
          </span>{' '}
          <span className="text-foreground text-sm">{title}</span>
        </div>
        {posting_date && (
          <time className="text-muted-foreground text-xs">
            {formatDate(posting_date)}
          </time>
        )}
      </div>
    </article>
  );
}
