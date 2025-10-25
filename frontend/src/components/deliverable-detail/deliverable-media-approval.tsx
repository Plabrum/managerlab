'use client';

import { DeliverablePreview } from '@/components/deliverable-preview/deliverable-preview';
import { MediaComments } from '@/components/media-comments';
import { SimpleMediaGallery } from '@/components/deliverable-preview/media-gallery-simple';
import type {
  DeliverableResponseSchema,
  DeliverableMediaAssociationSchema,
} from '@/openapi/managerLab.schemas';

interface DeliverableMediaApprovalProps {
  deliverable: DeliverableResponseSchema;
}

export function DeliverableMediaApproval({
  deliverable,
}: DeliverableMediaApprovalProps) {
  return (
    <div className="space-y-6">
      {/* Two Column Grid - Preview left, Comments right */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Left Column - Preview */}
        <div className="flex justify-center">
          <DeliverablePreview
            deliverable={deliverable}
            mediaAssociations={deliverable.deliverable_media_associations}
            roster={deliverable.assigned_roster}
          />
          <SimpleMediaGallery
            media={deliverable.deliverable_media_associations.map(
              (dm: DeliverableMediaAssociationSchema) => dm.media
            )}
          />
        </div>

        {/* Right Column - Comments */}
        <MediaComments />
      </div>
    </div>
  );
}
