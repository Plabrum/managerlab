'use client';

import { useState } from 'react';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList } from '@/components/object-list';

export default function BrandContactsPage() {
  const [currentViewId, setCurrentViewId] = useState<unknown | null>(null);

  return (
    <PageTopBar title="Brand Contacts">
      <ObjectList
        objectType="brandcontacts"
        currentViewId={currentViewId}
        onViewSelect={setCurrentViewId}
      />
    </PageTopBar>
  );
}
