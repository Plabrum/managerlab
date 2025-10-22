'use client';

import { use } from 'react';
import { ObjectFields, ObjectRelations } from '@/components/object-detail';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { DetailPageLayout } from '@/components/detail-page-layout';
import { ActionGroupType } from '@/openapi/managerLab.schemas';

export default function CampaignDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('campaigns', id);

  return (
    <DetailPageLayout
      title={data.title}
      state={data.state}
      createdAt={data.created_at}
      updatedAt={data.updated_at}
      actions={data.actions}
      actionGroup={ActionGroupType.campaign_actions}
      objectId={id}
      objectData={data}
    >
      <div className="container mx-auto py-6">
        <div className="space-y-6">
          {/* Two Column Grid */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Left Column - Fields */}
            <ObjectFields fields={data.fields} />
          </div>

          {/* Relations */}
          <ObjectRelations relations={data.relations || []} />
        </div>
      </div>
    </DetailPageLayout>
  );
}
