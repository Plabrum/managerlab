import { useState } from 'react';
import { DeliverablePreview } from '@/components/deliverable-preview/deliverable-preview';
import { SimpleMediaGallery } from '@/components/deliverable-preview/media-gallery-simple';
import { useAuth } from '@/components/providers/auth-provider';
import { MediaApprovalActions } from './media-approval-actions';
import { MediaThreadList } from './media-thread-list';
import type { DeliverableResponseSchema } from '@/openapi/ariveAPI.schemas';

interface DeliverableMediaApprovalProps {
  deliverable: DeliverableResponseSchema;
  onRefetch?: () => void;
}

export function DeliverableMediaApproval({
  deliverable,
  onRefetch,
}: DeliverableMediaApprovalProps) {
  const { user } = useAuth();
  const [focusedIndex, setFocusedIndex] = useState(0);

  const mediaAssociations = deliverable.deliverable_media_associations || [];
  const focusedMedia = mediaAssociations[focusedIndex];

  if (mediaAssociations.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-muted-foreground text-sm">
          No media uploaded for this deliverable yet.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Two Column Grid - Preview/Gallery left, Actions/Comments right */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Left Column - Preview stacked on Gallery */}
        <div className="flex flex-col space-y-6">
          <DeliverablePreview
            deliverable={deliverable}
            mediaAssociation={focusedMedia}
            roster={deliverable.assigned_roster}
          />
          <SimpleMediaGallery
            media={mediaAssociations.map((dm) => dm.media)}
            selectedIndex={focusedIndex}
            onMediaSelect={setFocusedIndex}
          />
        </div>

        {/* Right Column - Actions and Thread List */}
        <div className="flex flex-col space-y-4">
          {focusedMedia && (
            <MediaApprovalActions
              mediaAssociation={focusedMedia}
              onActionComplete={onRefetch}
            />
          )}
          <MediaThreadList
            mediaAssociations={mediaAssociations}
            currentUserId={user.id as string}
            focusedIndex={focusedIndex}
          />
        </div>
      </div>
    </div>
  );
}
