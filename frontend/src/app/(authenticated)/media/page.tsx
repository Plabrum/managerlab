import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function MediaPage() {
  return (
    <PageTopBar
      title="Media"
      actions={<TopLevelActions actionGroup={ActionGroupType.media_actions} />}
    >
      <ObjectList objectType="media" />
    </PageTopBar>
  );
}
