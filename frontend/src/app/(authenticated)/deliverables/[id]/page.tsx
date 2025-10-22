'use client';

import { use } from 'react';
import { useDeliverablesIdGetDeliverableSuspense } from '@/openapi/deliverables/deliverables';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { DetailPageLayout } from '@/components/detail-page-layout';
import { DeliverablePreview } from '@/components/deliverable-preview/deliverable-preview';
import { MediaComments } from '@/components/media-comments';
import { SimpleMediaGallery } from '@/components/deliverable-preview/media-gallery-simple';

export default function DeliverableDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  // New endpoint: Type-safe deliverable with relations
  const { data: deliverable } = useDeliverablesIdGetDeliverableSuspense(id);

  // Old endpoint: ObjectDetailDTO for action system compatibility
  // TODO: Remove once action system is migrated to use domain-specific schemas
  const { data: objectDetail } = useOObjectTypeIdGetObjectDetailSuspense(
    'deliverables',
    id
  );

  return (
    <DetailPageLayout
      title={deliverable.title}
      state={deliverable.state}
      createdAt={deliverable.created_at}
      updatedAt={deliverable.updated_at}
      actions={objectDetail.actions}
      actionGroup="deliverable_actions"
      objectId={id}
      objectData={objectDetail}
    >
      <div className="container mx-auto py-6">
        <div className="space-y-6">
          {/* Two Column Grid - Preview left, Comments right */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 ">
            {/* Left Column - Preview */}
            <div className="flex justify-center">
              <DeliverablePreview
                deliverable={deliverable}
                mediaAssociations={deliverable.deliverable_media_associations}
                roster={deliverable.assigned_roster}
              />
            </div>

            {/* Right Column - Comments */}
            <MediaComments />
          </div>

          {/* Media Gallery - Full Width at Bottom */}
          {deliverable.deliverable_media_associations.length > 0 && (
            <SimpleMediaGallery
              media={deliverable.deliverable_media_associations.map(
                (dm) => dm.media
              )}
            />
          )}
        </div>
      </div>
    </DetailPageLayout>
  );
}
