import { useEffect, useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import { EmptyState } from '@/components/empty-state';
import { PageTopBar } from '@/components/page-topbar';
import { useActionExecutor } from '@/hooks/use-action-executor';
import { useActionFormRenderer } from '@/hooks/use-action-form-renderer';
import { useDashboardsListDashboardsSuspense } from '@/openapi/dashboards/dashboards';
import type { ActionDTO } from '@/openapi/ariveAPI.schemas';

export function DashboardPage() {
  const navigate = useNavigate();
  const [hasRedirected, setHasRedirected] = useState(false);

  // Fetch dashboards using Suspense query - loading state handled by route's pendingComponent
  const { data: dashboards } = useDashboardsListDashboardsSuspense();

  // Setup action executor for dashboard creation
  const formRenderer = useActionFormRenderer();
  const executor = useActionExecutor({
    actionGroup: 'dashboard_actions',
    renderActionForm: formRenderer,
    onSuccess: (_action, response) => {
      // Redirect to the newly created dashboard
      if (response.created_id) {
        navigate({
          to: '/dashboard/$id',
          params: { id: String(response.created_id) },
        });
      }
    },
  });

  // Redirect to first dashboard if available
  useEffect(() => {
    if (!hasRedirected && dashboards.length > 0) {
      const firstDashboard =
        dashboards.find((d) => d.is_default) || dashboards[0];
      setHasRedirected(true);
      navigate({
        to: '/dashboard/$id',
        params: { id: String(firstDashboard.id) },
      });
    }
  }, [dashboards, hasRedirected, navigate]);

  // Create action DTO for dashboard creation
  const createDashboardAction: ActionDTO = {
    action: 'dashboard_actions__create',
    label: 'Create Dashboard',
    action_group_type: 'dashboard_actions',
    is_bulk_allowed: false,
    available: true,
    priority: 1,
  };

  // If no dashboards exist, show empty state (this will briefly show before redirect if dashboards exist)
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
