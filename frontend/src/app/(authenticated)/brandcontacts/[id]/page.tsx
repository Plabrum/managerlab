'use client';

import { use } from 'react';
import { ObjectFields, ObjectRelations } from '@/components/object-detail';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { PageTopBar } from '@/components/page-topbar';

export default function BrandContactDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('brandcontacts', id);

  return (
    <PageTopBar title={data.title} state={data.state}>
      <div className="space-y-6">
        {/* Fields */}
        <ObjectFields fields={data.fields} />

        {/* Relations */}
        <ObjectRelations relations={data.relations || []} />
      </div>
    </PageTopBar>
  );
}
