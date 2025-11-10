'use client';

import { MediaThreadCard } from './media-thread-card';
import type { DeliverableMediaAssociationSchema } from '@/openapi/ariveAPI.schemas';

interface MediaThreadListProps {
  mediaAssociations: DeliverableMediaAssociationSchema[];
  currentUserId: string;
  focusedIndex?: number;
}

export function MediaThreadList({
  mediaAssociations,
  currentUserId,
  focusedIndex,
}: MediaThreadListProps) {
  if (mediaAssociations.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-muted-foreground text-sm">
          No media items to display comments for.
        </p>
      </div>
    );
  }

  return (
    <div className="max-h-[600px] space-y-2 overflow-y-auto">
      {mediaAssociations.map((mediaAssociation, index) => (
        <MediaThreadCard
          key={mediaAssociation.media.id as string}
          mediaAssociation={mediaAssociation}
          mediaIndex={index + 1}
          currentUserId={currentUserId}
          defaultOpen={index === focusedIndex}
        />
      ))}
    </div>
  );
}
