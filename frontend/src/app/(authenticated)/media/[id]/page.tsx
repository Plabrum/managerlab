'use client';

import { use, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import {
  ObjectHeader,
  ObjectActions,
  ObjectFields,
  ObjectParents,
  ObjectChildren,
} from '@/components/object-detail';
import { MediaViewer } from '@/components/media-viewer';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { useBreadcrumb } from '@/components/breadcrumb-provider';
import type {
  ObjectFieldDTO,
  ImageFieldValue,
} from '@/openapi/managerLab.schemas';

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
  const pathname = usePathname();
  const { setBreadcrumb, clearBreadcrumb } = useBreadcrumb();

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('media', id);

  // Set breadcrumb title after data loads
  useEffect(() => {
    setBreadcrumb(pathname, data?.title);
    return () => {
      clearBreadcrumb(pathname);
    };
  }, [data?.title, pathname, setBreadcrumb, clearBreadcrumb]);

  const handleActionClick = (action: string) => {
    console.log('Action clicked:', action, 'on media:', id);
    // TODO: Implement action handlers
  };

  // Find the image field with proper type narrowing
  const imageField = data.fields.find(isImageField);

  // Get non-image fields
  const otherFields = data.fields.filter((field) => !isImageField(field));

  return (
    <div className="container mx-auto py-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <ObjectHeader
            title={data.title}
            state={data.state}
            createdAt={data.created_at}
            updatedAt={data.updated_at}
          />
          <ObjectActions
            actions={data.actions}
            onActionClick={handleActionClick}
          />
        </div>

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

        {/* Parents */}
        <ObjectParents parents={data.parents || []} />

        {/* Children */}
        {data.children && <ObjectChildren items={data.children} />}
      </div>
    </div>
  );
}
