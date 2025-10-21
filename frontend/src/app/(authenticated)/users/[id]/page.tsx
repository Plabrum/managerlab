'use client';

import { use } from 'react';
import {
  ObjectFields,
  ObjectParents,
  ObjectChildren,
} from '@/components/object-detail';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { DetailPageLayout } from '@/components/detail-page-layout';

export default function UserDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('users', id);

  return (
    <DetailPageLayout
      title={data.title}
      state={data.state}
      createdAt={data.created_at}
      updatedAt={data.updated_at}
    >
      <div className="container mx-auto py-6">
        <div className="space-y-6">
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
