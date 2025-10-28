import { ActionGroupType } from '@/openapi/managerLab.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function DeliverablesPage() {
  return (
    <PageTopBar
      title="Deliverables"
      actions={
        <TopLevelActions
          actionGroup={ActionGroupType.top_level_deliverable_actions}
        />
      }
    >
      <ObjectList objectType="deliverables" />
    </PageTopBar>
  );
}
