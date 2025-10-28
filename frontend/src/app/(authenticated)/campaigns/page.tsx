import { ActionGroupType } from '@/openapi/managerLab.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function CampaignsPage() {
  return (
    <PageTopBar
      title="Campaigns"
      actions={
        <TopLevelActions
          actionGroup={ActionGroupType.top_level_campaign_actions}
        />
      }
    >
      <ObjectList objectType="campaigns" />
    </PageTopBar>
  );
}
