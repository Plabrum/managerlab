'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { EmptyState } from '@/components/empty-state';
import { PageTopBar } from '@/components/page-topbar';
import { dashboardsListDashboards } from '@/openapi/dashboards/dashboards';
import { useActionExecutor } from '@/hooks/use-action-executor';
import { useActionFormRenderer } from '@/hooks/use-action-form-renderer';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import type { ActionDTO } from '@/openapi/ariveAPI.schemas';

export default function DashboardPage() {
  const router = useRouter();

  // Setup action executor for dashboard creation
  const formRenderer = useActionFormRenderer();
  const executor = useActionExecutor({
    actionGroup: 'dashboard_actions',
    renderActionForm: formRenderer,
    onSuccess: (action, response) => {
      // Redirect to the newly created dashboard
      if (response.created_id) {
        router.push(`/dashboard/${response.created_id}`);
      }
    },
  });

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

  // Create action DTO for dashboard creation
  const createDashboardAction: ActionDTO = {
    action: 'dashboard_actions__create',
    label: 'Create Dashboard',
    action_group_type: 'dashboard_actions',
    is_bulk_allowed: false,
    available: true,
    priority: 1,
  };

  // If no dashboards exist, show empty state
  return (
    <>
      <PageTopBar title="Dashboard">
        <div className="container mx-auto space-y-6 p-6">
          <EmptyState
            title="Create your first dashboard to start visualizing your data"
            cta={{
              label: 'Create Dashboard',
              onClick: () => executor.initiateAction(createDashboardAction),
            }}
            className="rounded-lg border-2 border-dashed py-12"
          />
        </div>
      </PageTopBar>

      <ActionConfirmationDialog
        open={executor.showConfirmation}
        action={executor.pendingAction}
        isExecuting={executor.isExecuting}
        onConfirm={executor.confirmAction}
        onCancel={executor.cancelAction}
      />

      {executor.pendingAction &&
        executor.renderActionForm &&
        executor.renderActionForm({
          action: executor.pendingAction,
          onSubmit: executor.executeWithData,
          onClose: executor.cancelAction,
          isSubmitting: executor.isExecuting,
          isOpen: executor.showForm,
          actionLabel: executor.pendingAction.label,
        })}
    </>
  );
}
