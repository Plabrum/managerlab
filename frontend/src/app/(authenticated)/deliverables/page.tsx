import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function DeliverablesPage() {
  return (
    <PageTopBar
      title="Deliverables"
      actions={
        <TopLevelActions actionGroup={ActionGroupType.deliverable_actions} />
      }
    >
      <ObjectList objectType="deliverables" />
    </PageTopBar>
  );
}
