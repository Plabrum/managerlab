'use client';

import { useState } from 'react';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function BrandsPage() {
  const [currentViewId, setCurrentViewId] = useState<unknown | null>(null);

  return (
    <PageTopBar
      title="Brands"
      actions={<TopLevelActions actionGroup={ActionGroupType.brand_actions} />}
    >
      <ObjectList
        objectType="brands"
        currentViewId={currentViewId}
        onViewSelect={setCurrentViewId}
      />
    </PageTopBar>
  );
}
