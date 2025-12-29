import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { ObjectList, TopLevelActions } from '@/components/object-list';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';

export const Route = createFileRoute('/_authenticated/campaigns/')({
  component: CampaignsPage,
});

function CampaignsPage() {
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
