import { ActionGroupType } from '@/openapi/managerLab.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function MediaPage() {
  return (
    <PageTopBar
      title="Media"
      actions={
        <TopLevelActions
          actionGroup={ActionGroupType.top_level_media_actions}
        />
      }
    >
      <ObjectList objectType="media" />
    </PageTopBar>
  );
}
