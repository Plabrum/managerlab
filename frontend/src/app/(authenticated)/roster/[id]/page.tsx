'use client';

import { use } from 'react';
import { ObjectFields, ObjectRelations } from '@/components/object-detail';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { DetailPageLayout } from '@/components/detail-page-layout';

export default function RosterDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('roster', id);

  return (
    <DetailPageLayout title={data.title} state={data.state}>
      <div className="container mx-auto py-6">
        <div className="space-y-6">
          {/* Fields */}
          <ObjectFields fields={data.fields} />

          {/* Relations */}
          <ObjectRelations relations={data.relations || []} />
        </div>
      </div>
    </DetailPageLayout>
  );
}
