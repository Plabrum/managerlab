import { useState } from 'react';
import { ObjectList, TopLevelActions } from '@/components/object-list';
import { PageTopBar } from '@/components/page-topbar';
import { createListPageMeta } from '@/lib/meta-helpers';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';

export function CampaignsPage() {
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
