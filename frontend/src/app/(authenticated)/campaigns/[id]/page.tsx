'use client';

import { use } from 'react';
import { ObjectActions } from '@/components/object-detail';
import { CampaignFields } from '@/components/campaign-detail';
import { useCampaignsIdGetCampaignSuspense } from '@/openapi/campaigns/campaigns';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/managerLab.schemas';

export default function CampaignDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data, refetch } = useCampaignsIdGetCampaignSuspense(id, {});

  return (
    <PageTopBar
      title={data.name}
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
          <CampaignFields campaign={data} />
        </div>
      </div>
    </PageTopBar>
  );
}
