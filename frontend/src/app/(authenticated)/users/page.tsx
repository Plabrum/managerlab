'use client';

import { useState } from 'react';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList } from '@/components/object-list';

export default function UsersPage() {
  const [currentViewId, setCurrentViewId] = useState<unknown | null>(null);

  return (
    <PageTopBar title="Users">
      <ObjectList
        objectType="users"
        currentViewId={currentViewId}
        onViewSelect={setCurrentViewId}
      />
    </PageTopBar>
  );
}
