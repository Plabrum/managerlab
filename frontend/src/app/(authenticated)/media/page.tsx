'use client';

import { useState } from 'react';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function MediaPage() {
  const [currentViewId, setCurrentViewId] = useState<unknown | null>(null);

  return (
    <PageTopBar
      title="Media"
      actions={<TopLevelActions actionGroup={ActionGroupType.media_actions} />}
    >
      <ObjectList
        objectType="media"
        currentViewId={currentViewId}
        onViewSelect={setCurrentViewId}
      />
    </PageTopBar>
  );
}
