import { useRef, useCallback } from 'react';
import { useParams } from '@tanstack/react-router';
import { DashboardContent } from '@/components/dashboard/dashboard-content';
import { ObjectActions } from '@/components/object-detail';
import { PageTopBar } from '@/components/page-topbar';
import { useEditAction } from '@/hooks/use-edit-action';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { useDashboardsIdGetDashboardSuspense } from '@/openapi/dashboards/dashboards';

export function DashboardDetailPage() {
  const { id } = useParams({ from: '/_authenticated/dashboard/$id' });
  const { data: dashboard, refetch } = useDashboardsIdGetDashboardSuspense(id);

  // URL parameter-based edit mode with permission checking
  const { isEditMode, openEdit, closeEdit } = useEditAction({
    actions: dashboard.actions || [],
  });

  // Ref to store the finish editing handler from DashboardContent
  const finishEditingHandlerRef = useRef<(() => Promise<void>) | null>(null);

  // Register the handler from DashboardContent
  const registerFinishHandler = useCallback((handler: () => Promise<void>) => {
    finishEditingHandlerRef.current = handler;
  }, []);

  // Enhanced close handler that saves before closing
  const handleCloseEdit = useCallback(async () => {
    if (finishEditingHandlerRef.current) {
      await finishEditingHandlerRef.current();
    } else {
      closeEdit();
    }
  }, [closeEdit]);

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
            onClose: handleCloseEdit,
          }}
        />
      }
    >
      <DashboardContent
        dashboard={dashboard}
        onUpdate={refetch}
        isEditMode={isEditMode}
        onCloseEditMode={closeEdit}
        onRegisterFinishHandler={registerFinishHandler}
      />
    </PageTopBar>
  );
}
