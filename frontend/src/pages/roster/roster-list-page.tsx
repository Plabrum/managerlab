import { useState } from 'react';
import { ObjectList, TopLevelActions } from '@/components/object-list';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';

export function RosterPage() {
  const [currentViewId, setCurrentViewId] = useState<unknown | null>(null);

  return (
    <PageTopBar
      title="Roster"
      actions={<TopLevelActions actionGroup={ActionGroupType.roster_actions} />}
    >
      <ObjectList
        objectType="roster"
        currentViewId={currentViewId}
        onViewSelect={setCurrentViewId}
      />
    </PageTopBar>
  );
}
