'use client';

import { use, useMemo } from 'react';
import {
  useDeliverablesIdGetDeliverableSuspense,
  getDeliverablesIdGetDeliverableQueryKey,
} from '@/openapi/deliverables/deliverables';
import {
  useOObjectTypeIdGetObjectDetailSuspense,
  getOObjectTypeIdGetObjectDetailQueryKey,
} from '@/openapi/objects/objects';
import { DetailPageLayout } from '@/components/detail-page-layout';
import { DeliverablePreview } from '@/components/deliverable-preview/deliverable-preview';
import { MediaComments } from '@/components/media-comments';
import { SimpleMediaGallery } from '@/components/deliverable-preview/media-gallery-simple';
import type { ActionData } from '@/components/header-provider';

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

  // Create actionsData with invalidation callback
  const actionsData: ActionData | undefined = useMemo(() => {
    if (!objectDetail.actions) return undefined;

    return {
      actions: objectDetail.actions,
      actionGroup: 'deliverable_actions' as const,
      objectId: id,
      objectData: objectDetail,
      onInvalidate: (queryClient) => {
        // Invalidate deliverable detail query
        queryClient.invalidateQueries({
          queryKey: getDeliverablesIdGetDeliverableQueryKey(id),
        });
        // Invalidate object detail query
        queryClient.invalidateQueries({
          queryKey: getOObjectTypeIdGetObjectDetailQueryKey('deliverables', id),
        });
      },
    };
  }, [objectDetail, id]);

  return (
    <DetailPageLayout
      title={deliverable.title}
      state={deliverable.state}
      actionsData={actionsData}
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
              <SimpleMediaGallery
                media={deliverable.deliverable_media_associations.map(
                  (dm) => dm.media
                )}
              />
            </div>

            {/* Right Column - Comments */}
            <MediaComments />
          </div>
        </div>
      </div>
    </DetailPageLayout>
  );
}
