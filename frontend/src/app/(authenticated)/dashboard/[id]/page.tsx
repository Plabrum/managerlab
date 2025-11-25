'use client';

import { use } from 'react';
import { useDashboardsIdGetDashboardSuspense } from '@/openapi/dashboards/dashboards';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { ObjectActions } from '@/components/object-detail';
import { DashboardContent } from '@/components/dashboard/dashboard-content';
import { useEditAction } from '@/hooks/use-edit-action';

export default function DashboardByIdPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: dashboard, refetch } = useDashboardsIdGetDashboardSuspense(id);

  // URL parameter-based edit mode with permission checking
  const { isEditMode, openEdit, closeEdit } = useEditAction({
    actions: dashboard.actions || [],
  });

  return (
    <PageTopBar
      title={dashboard.name}
      actions={
        <ObjectActions
          data={dashboard}
          actionGroup={ActionGroupType.dashboard_actions}
          onRefetch={refetch}
          editMode={{
            isOpen: isEditMode,
            onOpen: openEdit,
            onClose: closeEdit,
          }}
        />
      }
    >
      <DashboardContent
        dashboard={dashboard}
        onUpdate={refetch}
        isEditMode={isEditMode}
        onCloseEditMode={closeEdit}
      />
    </PageTopBar>
  );
}
