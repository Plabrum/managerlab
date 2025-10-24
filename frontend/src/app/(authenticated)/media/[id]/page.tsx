'use client';

import { use } from 'react';
import {
  ObjectFields,
  ObjectRelations,
  ObjectActions,
} from '@/components/object-detail';
import { MediaViewer } from '@/components/media-viewer';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { PageTopBar } from '@/components/page-topbar';
import type {
  ObjectFieldDTO,
  ImageFieldValue,
} from '@/openapi/managerLab.schemas';
import { ActionGroupType } from '@/openapi/managerLab.schemas';

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

  const { data, refetch } = useOObjectTypeIdGetObjectDetailSuspense(
    'media',
    id
  );

  // Find the image field with proper type narrowing
  const imageField = data.fields.find(isImageField);

  // Get non-image fields
  const otherFields = data.fields.filter((field) => !isImageField(field));

  return (
    <PageTopBar
      title={data.title}
      state={data.state}
      actions={
        <ObjectActions
          data={data}
          actionGroup={ActionGroupType.media_actions}
          onRefetch={refetch}
        />
      }
    >
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
    </PageTopBar>
  );
}
