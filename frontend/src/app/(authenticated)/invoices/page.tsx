import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function InvoicesPage() {
  return (
    <PageTopBar
      title="Invoices"
      actions={
        <TopLevelActions actionGroup={ActionGroupType.invoice_actions} />
      }
    >
      <ObjectList objectType="invoices" />
    </PageTopBar>
  );
}
