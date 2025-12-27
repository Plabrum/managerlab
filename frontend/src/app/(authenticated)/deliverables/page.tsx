'use client';

import { useState } from 'react';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function DeliverablesPage() {
  const [currentViewId, setCurrentViewId] = useState<unknown | null>(null);

  return (
    <PageTopBar
      title="Deliverables"
      actions={
        <TopLevelActions actionGroup={ActionGroupType.deliverable_actions} />
      }
    >
      <ObjectList
        objectType="deliverables"
        currentViewId={currentViewId}
        onViewSelect={setCurrentViewId}
      />
    </PageTopBar>
  );
}
