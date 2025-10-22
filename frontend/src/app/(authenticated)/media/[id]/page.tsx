'use client';

import { use, useMemo } from 'react';
import { ObjectFields, ObjectRelations } from '@/components/object-detail';
import { MediaViewer } from '@/components/media-viewer';
import {
  useOObjectTypeIdGetObjectDetailSuspense,
  getOObjectTypeIdGetObjectDetailQueryKey,
} from '@/openapi/objects/objects';
import { DetailPageLayout } from '@/components/detail-page-layout';
import type {
  ObjectFieldDTO,
  ImageFieldValue,
} from '@/openapi/managerLab.schemas';
import { ActionGroupType } from '@/openapi/managerLab.schemas';
import type { ActionData } from '@/components/header-provider';

// Type guard to check if a field value is an ImageFieldValue
function isImageField(
  field: ObjectFieldDTO
): field is ObjectFieldDTO & { value: ImageFieldValue } {
  return (
    typeof field.value === 'object' &&
    field.value !== null &&
    'type' in field.value &&
    field.value.type === 'image'
  );
}

export default function MediaDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('media', id);

  // Find the image field with proper type narrowing
  const imageField = data.fields.find(isImageField);

  // Get non-image fields
  const otherFields = data.fields.filter((field) => !isImageField(field));

  const actionsData: ActionData | undefined = useMemo(() => {
    if (!data.actions) return undefined;

    return {
      actions: data.actions,
      actionGroup: ActionGroupType.media_actions,
      objectId: id,
      objectData: data,
      onInvalidate: (queryClient) => {
        queryClient.invalidateQueries({
          queryKey: getOObjectTypeIdGetObjectDetailQueryKey('media', id),
        });
      },
    };
  }, [data, id]);

  return (
    <DetailPageLayout
      title={data.title}
      state={data.state}
      actionsData={actionsData}
    >
      <div className="container mx-auto py-6">
        <div className="space-y-6">
          {/* Two Column Grid - only when image exists */}
          {imageField ? (
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {/* Left Column - Fields */}
              <ObjectFields fields={otherFields} />

              {/* Right Column - Media Viewer */}
              <MediaViewer url={imageField.value.url} alt={data.title} />
            </div>
          ) : (
            /* Full width when no image */
            <ObjectFields fields={otherFields} />
          )}

          {/* Relations */}
          <ObjectRelations relations={data.relations || []} />
        </div>
      </div>
    </DetailPageLayout>
  );
}
