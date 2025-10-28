import { ActionGroupType } from '@/openapi/managerLab.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function RosterPage() {
  return (
    <PageTopBar
      title="Roster"
      actions={
        <TopLevelActions
          actionGroup={ActionGroupType.top_level_roster_actions}
        />
      }
    >
      <ObjectList objectType="roster" />
    </PageTopBar>
  );
}
