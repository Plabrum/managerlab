'use client';

import { use } from 'react';
import { ObjectActions } from '@/components/object-detail';
import { BrandFields } from '@/components/brand-detail';
import { useBrandsIdGetBrandSuspense } from '@/openapi/brands/brands';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/managerLab.schemas';
import { ChatButton } from '@/components/chat-button';
import { ChatDrawer } from '@/components/chat-drawer';
import { useAuth } from '@/components/providers/auth-provider';

export default function BrandDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { user } = useAuth();
  const [isChatOpen, setIsChatOpen] = useState(false);

  const { data, refetch } = useBrandsIdGetBrandSuspense(id);

  // Note: ObjectDetailDTO has thread_id but doesn't include unread count
  // We'll show the chat button but without unread count for now
  const unreadCount = 0; // TODO: Fetch unread count separately if needed

  return (
    <>
      <PageTopBar
        title={data.title}
        state={data.state}
        chatButton={
          <ChatButton
            unreadCount={unreadCount}
            onClick={() => setIsChatOpen(true)}
          />
        }
        actions={
          <ObjectActions
            data={data}
            actionGroup={ActionGroupType.brand_actions}
            onRefetch={refetch}
          />
        }
      >
        <div className="space-y-6">
          {/* Two Column Grid */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Left Column - Fields */}
            <ObjectFields fields={data.fields} />
          </div>

          {/* Relations */}
          <ObjectRelations relations={data.relations || []} />
        </div>
      </PageTopBar>

      <ChatDrawer
        open={isChatOpen}
        onOpenChange={setIsChatOpen}
        threadableType="brands"
        threadableId={parseInt(id, 10)}
        currentUserId={user.id as string}
        title={`Chat - ${data.title}`}
      />
    </>
  );
}
