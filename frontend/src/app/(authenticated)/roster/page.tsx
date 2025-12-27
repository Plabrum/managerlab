'use client';

import { useState } from 'react';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function RosterPage() {
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
