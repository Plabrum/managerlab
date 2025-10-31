import { PageTopBar } from '@/components/page-topbar';
import { ObjectList } from '@/components/object-list';

export default function BrandContactsPage() {
  return (
    <PageTopBar title="Brand Contacts">
      <ObjectList objectType="brandcontacts" />
    </PageTopBar>
  );
}
