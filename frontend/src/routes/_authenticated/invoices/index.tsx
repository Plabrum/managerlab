import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { ObjectList, TopLevelActions } from '@/components/object-list';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';

export const Route = createFileRoute('/_authenticated/invoices/')({
  component: InvoicesPage,
});

function InvoicesPage() {
  const [currentViewId, setCurrentViewId] = useState<unknown | null>(null);

  return (
    <PageTopBar
      title="Invoices"
      actions={
        <TopLevelActions actionGroup={ActionGroupType.invoice_actions} />
      }
    >
      <ObjectList
        objectType="invoices"
        currentViewId={currentViewId}
        onViewSelect={setCurrentViewId}
      />
    </PageTopBar>
  );
}
