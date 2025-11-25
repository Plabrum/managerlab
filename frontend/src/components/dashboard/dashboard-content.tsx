'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { useQueryClient } from '@tanstack/react-query';
import { WidgetContainer } from './widget-container';
import { DashboardEditMode } from './dashboard-edit-mode';
import { CreateWidgetForm } from './create-widget-form';
import { widgetRegistry } from '@/lib/widgets/registry';
import { useActionsActionGroupExecuteAction } from '@/openapi/actions/actions';
import {
  ActionGroupType,
  type CreateWidgetSchema,
  type DashboardSchema,
  type ReorderWidgetsSchema,
  type WidgetSchema,
} from '@/openapi/ariveAPI.schemas';
import type { WidgetType, WidgetQuery } from '@/types/dashboard';

interface DashboardContentProps {
  dashboard: DashboardSchema;
  onUpdate: () => void;
  isEditMode: boolean;
  onCloseEditMode?: () => void;
}

export function DashboardContent({
  dashboard,
  onUpdate,
  isEditMode,
  onCloseEditMode,
}: DashboardContentProps) {
  const queryClient = useQueryClient();
  const [createFormOpen, setCreateFormOpen] = useState(false);
  const [prefilledType, setPrefilledType] = useState<WidgetType | null>(null);

  // Use widgets from the new relationship
  const widgets = dashboard.widgets || [];

  // Mutations for widget operations
  const createWidgetMutation = useActionsActionGroupExecuteAction();
  const reorderWidgetsMutation = useActionsActionGroupExecuteAction();

  const handleWidgetDrop = (widgetType: WidgetType) => {
    setPrefilledType(widgetType);
    setCreateFormOpen(true);
  };

  const handleCreateWidget = async (data: CreateWidgetSchema) => {
    try {
      await createWidgetMutation.mutateAsync({
        actionGroup: ActionGroupType.widget_actions,
        data: {
          action: 'widget_actions__create',
          data,
        },
      });
      toast.success('Widget created successfully');
      setCreateFormOpen(false);
      setPrefilledType(null);
      // Invalidate queries to refresh dashboard
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });
      onUpdate();
    } catch (error) {
      console.error('Failed to create widget:', error);
      toast.error('Failed to create widget');
    }
  };

  const handleWidgetReorder = async (reorderedWidgets: WidgetSchema[]) => {
    // Build the reorder data with position based on array index
    const reorderData: ReorderWidgetsSchema = {
      dashboard_id: dashboard.id as string,
      widgets: reorderedWidgets.map((widget, index) => ({
        id: widget.id as string,
        position_x: index,
        position_y: 0, // For now, single-row layout
      })),
    };

    try {
      await reorderWidgetsMutation.mutateAsync({
        actionGroup: ActionGroupType.widget_actions,
        data: {
          action: 'widget_actions__reorder',
          data: reorderData,
        },
      });
      // Silently succeed - the UI already shows the new order
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });
    } catch (error) {
      console.error('Failed to reorder widgets:', error);
      toast.error('Failed to save widget order');
      // Refresh to reset to server state
      onUpdate();
    }
  };

  const renderWidget = (widget: WidgetSchema) => {
    const entry = widgetRegistry[widget.type as WidgetType];
    if (!entry) {
      return <div>Unknown widget type</div>;
    }
    const Component = entry.component;
    // Cast query to WidgetQuery since the generated type is more permissive
    return <Component query={widget.query as unknown as WidgetQuery} />;
  };

  return (
    <>
      <DashboardEditMode
        isEditMode={isEditMode}
        widgets={widgets}
        onWidgetDrop={handleWidgetDrop}
        onWidgetReorder={handleWidgetReorder}
        onClose={onCloseEditMode}
      >
        {({ renderWidgetWrapper }) => (
          <>
            {widgets.length === 0 ? (
              <div className="container mx-auto p-6">
                <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed py-12">
                  <p className="text-muted-foreground">
                    {isEditMode
                      ? 'Drag a widget from the sidebar to get started'
                      : 'No widgets configured. Enable edit mode to add widgets.'}
                  </p>
                </div>
              </div>
            ) : (
              widgets.map((widget, index) =>
                renderWidgetWrapper(
                  widget,
                  index,
                  <WidgetContainer
                    widget={widget}
                    onRefetch={onUpdate}
                    isEditMode={isEditMode}
                  >
                    {renderWidget(widget)}
                  </WidgetContainer>
                )
              )
            )}
          </>
        )}
      </DashboardEditMode>

      <CreateWidgetForm
        isOpen={createFormOpen}
        onOpenChange={(open) => {
          if (!open) {
            setCreateFormOpen(false);
            setPrefilledType(null);
          }
        }}
        dashboardId={dashboard.id as string}
        prefilledType={prefilledType ?? undefined}
        onSubmit={handleCreateWidget}
        isSubmitting={createWidgetMutation.isPending}
        actionLabel="Add Widget"
      />
    </>
  );
}
