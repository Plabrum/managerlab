import { ActionGroupType } from '@/openapi/managerLab.schemas';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectList, TopLevelActions } from '@/components/object-list';

export default function BrandsPage() {
  return (
    <PageTopBar
      title="Brands"
      actions={
        <TopLevelActions
          actionGroup={ActionGroupType.top_level_brand_actions}
        />
      }
    >
      <ObjectList objectType="brands" />
    </PageTopBar>
  );
}
