'use client';

import { useState } from 'react';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function CampaignsPage() {
  const [currentViewId, setCurrentViewId] = useState<unknown | null>(null);

  return (
    <PageTopBar
      title="Campaigns"
      actions={
        <TopLevelActions actionGroup={ActionGroupType.campaign_actions} />
      }
    >
      <ObjectList
        objectType="campaigns"
        currentViewId={currentViewId}
        onViewSelect={setCurrentViewId}
      />
    </PageTopBar>
  );
}
