import { PageTopBar } from '@/components/page-topbar';
import { ObjectList } from '@/components/object-list';

export default function UsersPage() {
  return (
    <PageTopBar title="Users">
      <ObjectList objectType="users" />
    </PageTopBar>
  );
}
