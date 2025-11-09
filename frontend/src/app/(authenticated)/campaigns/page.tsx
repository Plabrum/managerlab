import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function CampaignsPage() {
  return (
    <PageTopBar
      title="Campaigns"
      actions={
        <TopLevelActions actionGroup={ActionGroupType.campaign_actions} />
      }
    >
      <ObjectList objectType="campaigns" />
    </PageTopBar>
  );
}
