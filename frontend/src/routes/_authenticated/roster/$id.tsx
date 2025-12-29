import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';
import ErrorPage from '@/routes/_public/error';
import { ActivityFeed } from '@/components/activity/activity-feed';
import { ObjectActions } from '@/components/object-detail';
import { ObjectDetailTabs } from '@/components/object-detail-tabs';
import { PageTopBar } from '@/components/page-topbar';
import { useAuth } from '@/components/providers/auth-provider';
import { RosterFields } from '@/components/roster-detail';
import { TabsContent } from '@/components/ui/tabs';
import { ActionGroupType, ObjectTypes } from '@/openapi/ariveAPI.schemas';
import { useRosterIdGetRosterSuspense } from '@/openapi/roster/roster';

const searchSchema = z.object({
  edit: z.boolean().optional(),
  tab: z.enum(['summary', 'activity']).optional().default('summary'),
});

export const Route = createFileRoute('/_authenticated/roster/$id')({
  component: RosterDetailPage,
  validateSearch: searchSchema,
  errorComponent: ({ error }) => {
    if (
      error &&
      typeof error === 'object' &&
      'status' in error &&
      error.status === 404
    ) {
      return <ErrorPage />;
    }
    throw error;
  },
});

function RosterDetailPage() {
  const { id } = Route.useParams();
  const { user } = useAuth();

  const { data, refetch } = useRosterIdGetRosterSuspense(id);

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
