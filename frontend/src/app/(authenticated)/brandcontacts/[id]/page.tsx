'use client';

import { use } from 'react';
import {
  ObjectHeader,
  ObjectFields,
  ObjectParents,
  ObjectChildren,
} from '@/components/object-detail';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { DetailPageLayout } from '@/components/detail-page-layout';

export default function BrandContactDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('brandcontacts', id);

  return (
    <DetailPageLayout objectTitle={data.title}>
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
            {/* TODO: Add ObjectActions when brandcontact_actions ActionGroupType is added to backend */}
          </div>

          {/* Fields */}
          <ObjectFields fields={data.fields} />

          {/* Parents */}
          <ObjectParents parents={data.parents || []} />

          {/* Children */}
          {data.children && <ObjectChildren items={data.children} />}
        </div>
      </div>
    </DetailPageLayout>
  );
}
