import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { ObjectList } from '@/components/object-list';
import { PageTopBar } from '@/components/page-topbar';

export const Route = createFileRoute('/_authenticated/brandcontacts/')({
  component: BrandContactsPage,
});

function BrandContactsPage() {
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
