import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { ObjectList } from '@/components/object-list';
import { PageTopBar } from '@/components/page-topbar';

export const Route = createFileRoute('/_authenticated/users/')({
  component: UsersPage,
});

function UsersPage() {
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
