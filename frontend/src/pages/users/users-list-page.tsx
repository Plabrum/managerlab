import { useState } from 'react';
import { ObjectList } from '@/components/object-list';
import { PageTopBar } from '@/components/page-topbar';

export function UsersPage() {
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
