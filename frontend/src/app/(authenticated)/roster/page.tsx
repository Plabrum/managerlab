import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function RosterPage() {
  return (
    <PageTopBar
      title="Roster"
      actions={<TopLevelActions actionGroup={ActionGroupType.roster_actions} />}
    >
      <ObjectList objectType="roster" />
    </PageTopBar>
  );
}
