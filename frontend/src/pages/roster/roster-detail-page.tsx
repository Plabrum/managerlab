import { useParams } from '@tanstack/react-router';
import { ActivityFeed } from '@/components/activity/activity-feed';
import { ObjectActions } from '@/components/object-detail';
import { ObjectDetailTabs } from '@/components/object-detail-tabs';
import { PageTopBar } from '@/components/page-topbar';
import { useAuth } from '@/components/providers/auth-provider';
import { RosterFields } from '@/components/roster-detail';
import { TabsContent } from '@/components/ui/tabs';
import { ActionGroupType, ObjectTypes } from '@/openapi/ariveAPI.schemas';
import { useRosterIdGetRosterSuspense } from '@/openapi/roster/roster';

export function RosterDetailPage() {
  const { id } = useParams({ from: '/_authenticated/roster/$id' });
  const { data, refetch } = useRosterIdGetRosterSuspense(id);
  const { user } = useAuth();

  return (
    <PageTopBar
      title={data.name}
      state={data.state}
      actions={
        <ObjectActions
          data={data}
          actionGroup={ActionGroupType.roster_actions}
          onRefetch={refetch}
        />
      }
    >
      <ObjectDetailTabs
        tabs={[
          { value: 'summary', label: 'Summary' },
          {
            value: 'activity',
            label: 'Activity',
            unreadCount: data.thread?.unread_count,
          },
        ]}
        defaultTab="summary"
      >
        <TabsContent value="summary" className="space-y-6">
          <div className="space-y-6">
            {/* Two Column Grid */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {/* Left Column - Fields */}
              <RosterFields roster={data} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="activity">
          <ActivityFeed
            threadableType={ObjectTypes.roster}
            threadableId={id}
            currentUserId={user.id as string}
          />
        </TabsContent>
      </ObjectDetailTabs>
    </PageTopBar>
  );
}
