'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { EmptyState } from '@/components/empty-state';
import { PageTopBar } from '@/components/page-topbar';
import { dashboardsListDashboards } from '@/openapi/dashboards/dashboards';

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    const redirectToDashboard = async () => {
      try {
        const dashboards = await dashboardsListDashboards();

        if (dashboards.length > 0) {
          const firstDashboard =
            dashboards.find((d) => d.is_default) || dashboards[0];
          router.replace(`/dashboard/${firstDashboard.id}`);
        }
      } catch (error) {
        console.error('Failed to fetch dashboards:', error);
      }
    };

    redirectToDashboard();
  }, [router]);

  // If no dashboards exist, show empty state
  return (
    <PageTopBar title="Dashboard">
      <div className="container mx-auto space-y-6 p-6">
        <EmptyState
          title="Create your first dashboard to start visualizing your data"
          cta={{
            label: 'Create Dashboard',
            onClick: () => {
              // TODO: Create dashboard via action when available
              console.log('Create dashboard');
            },
          }}
          className="rounded-lg border-2 border-dashed py-12"
        />
      </div>
    </PageTopBar>
  );
}
