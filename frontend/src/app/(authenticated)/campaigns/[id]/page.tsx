'use client';

import { use } from 'react';
import {
  ObjectFields,
  ObjectRelations,
  ObjectActions,
} from '@/components/object-detail';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/managerLab.schemas';

export default function CampaignDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data, refetch } = useOObjectTypeIdGetObjectDetailSuspense(
    'campaigns',
    id
  );

  return (
    <PageTopBar
      title={data.title}
      state={data.state}
      actions={
        <ObjectActions
          data={data}
          actionGroup={ActionGroupType.campaign_actions}
          onRefetch={refetch}
        />
      }
    >
      <div className="space-y-6">
        {/* Two Column Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Left Column - Fields */}
          <ObjectFields fields={data.fields} />
        </div>

        {/* Relations */}
        <ObjectRelations relations={data.relations || []} />
      </div>
    </PageTopBar>
  );
}
