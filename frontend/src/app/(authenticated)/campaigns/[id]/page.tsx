'use client';

import { use, useMemo } from 'react';
import { ObjectFields, ObjectRelations } from '@/components/object-detail';
import {
  useOObjectTypeIdGetObjectDetailSuspense,
  getOObjectTypeIdGetObjectDetailQueryKey,
} from '@/openapi/objects/objects';
import { DetailPageLayout } from '@/components/detail-page-layout';
import { ActionGroupType } from '@/openapi/managerLab.schemas';
import type { ActionData } from '@/components/header-provider';

export default function CampaignDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('campaigns', id);

  const actionsData: ActionData | undefined = useMemo(() => {
    if (!data.actions) return undefined;

    return {
      actions: data.actions,
      actionGroup: ActionGroupType.campaign_actions,
      objectId: id,
      objectData: data,
      onInvalidate: (queryClient) => {
        queryClient.invalidateQueries({
          queryKey: getOObjectTypeIdGetObjectDetailQueryKey('campaigns', id),
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
