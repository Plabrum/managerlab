'use client';

import { use, useState } from 'react';
import { useDeliverablesIdGetDeliverableSuspense } from '@/openapi/deliverables/deliverables';
import { PageTopBar } from '@/components/page-topbar';
import { DeliverablePreview } from '@/components/deliverable-preview/deliverable-preview';
import { MediaComments } from '@/components/media-comments';
import { SimpleMediaGallery } from '@/components/deliverable-preview/media-gallery-simple';
import { ObjectActions } from '@/components/object-detail';
import { ChatButton } from '@/components/chat-button';
import { ChatDrawer } from '@/components/chat-drawer';
import { useAuth } from '@/components/providers/auth-provider';

export default function DeliverableDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { user } = useAuth();
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Type-safe deliverable with relations and actions
  const { data, refetch } = useDeliverablesIdGetDeliverableSuspense(id);

  const unreadCount = data.thread?.unread_count ?? 0;

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
            actionGroup="deliverable_actions"
            onRefetch={refetch}
          />
        }
      >
        <div className="space-y-6">
          {/* Two Column Grid - Preview left, Comments right */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 ">
            {/* Left Column - Preview */}
            <div className="flex justify-center">
              <DeliverablePreview
                deliverable={data}
                mediaAssociations={data.deliverable_media_associations}
                roster={data.assigned_roster}
              />
              <SimpleMediaGallery
                media={data.deliverable_media_associations.map(
                  (dm) => dm.media
                )}
              />
            </div>

            {/* Right Column - Comments */}
            <MediaComments />
          </div>
        </div>
      </PageTopBar>

      <ChatDrawer
        open={isChatOpen}
        onOpenChange={setIsChatOpen}
        threadableType="deliverables"
        threadableId={parseInt(id, 10)}
        currentUserId={user.id as string}
        title={`Chat - ${data.title}`}
      />
    </>
  );
}
