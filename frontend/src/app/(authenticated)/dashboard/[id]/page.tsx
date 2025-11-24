'use client';

import { use } from 'react';
import { useDashboardsIdGetDashboardSuspense } from '@/openapi/dashboards/dashboards';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { ObjectActions } from '@/components/object-detail';
import { DashboardWidgets } from '@/components/dashboard/dashboard-widgets';

export default function DashboardByIdPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: dashboard, refetch } = useDashboardsIdGetDashboardSuspense(id);

  return (
    <PageTopBar
      title={dashboard.name}
      actions={
        <ObjectActions
          data={dashboard}
          actionGroup={ActionGroupType.dashboard_actions}
          onRefetch={refetch}
        />
      }
    >
      <DashboardWidgets dashboard={dashboard} onUpdate={refetch} />
    </PageTopBar>
  );
}
