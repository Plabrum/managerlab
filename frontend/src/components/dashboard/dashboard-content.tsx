import { useState, useCallback, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import {
  useActionsActionGroupExecuteAction,
  useActionsActionGroupObjectIdExecuteObjectAction,
} from '@/openapi/actions/actions';
import {
  ActionGroupType,
  type CreateWidgetSchema,
  type DashboardSchema,
} from '@/openapi/ariveAPI.schemas';
import { CreateWidgetForm } from './create-widget-form';
import { DashboardGrid } from './dashboard-grid';
import { DashboardWidgetPalette } from './dashboard-widget-palette';
import type { WidgetType } from '@/types/dashboard';
import type { Layouts } from 'react-grid-layout';

interface DashboardContentProps {
  dashboard: DashboardSchema;
  onUpdate: () => void;
  isEditMode: boolean;
  onCloseEditMode?: () => void;
  onRegisterFinishHandler?: (handler: () => Promise<void>) => void;
}

export function DashboardContent({
  dashboard,
  onUpdate,
  isEditMode,
  onCloseEditMode,
  onRegisterFinishHandler,
}: DashboardContentProps) {
  const queryClient = useQueryClient();
  const [createFormOpen, setCreateFormOpen] = useState(false);
  const [prefilledType, setPrefilledType] = useState<WidgetType | null>(null);
  const [draggingWidgetType, setDraggingWidgetType] =
    useState<WidgetType | null>(null);
  const [pendingLayout, setPendingLayout] = useState<Layouts | null>(null);
  const [pendingPosition, setPendingPosition] = useState<{
    x: number;
    y: number;
    w: number;
    h: number;
  } | null>(null);

  // Use widgets from the new relationship
  const widgets = dashboard.widgets || [];

  // Mutations for widget and dashboard operations
  const createWidgetMutation = useActionsActionGroupExecuteAction();
  const updateDashboardMutation =
    useActionsActionGroupObjectIdExecuteObjectAction();

  const handleWidgetClick = useCallback((widgetType: WidgetType) => {
    setPrefilledType(widgetType);
    setCreateFormOpen(true);
  }, []);

  const handleWidgetDragStart = useCallback((widgetType: WidgetType) => {
    setDraggingWidgetType(widgetType);
  }, []);

  const handleWidgetDragEnd = useCallback(() => {
    setDraggingWidgetType(null);
  }, []);

  const handleWidgetDropOnGrid = useCallback(
    (layout: { x: number; y: number; w: number; h: number }) => {
      if (!draggingWidgetType) return;

      // Open the create form with the widget type and position pre-filled
      setPrefilledType(draggingWidgetType);
      setPendingPosition(layout);
      setCreateFormOpen(true);
      setDraggingWidgetType(null);
    },
    [draggingWidgetType]
  );

  const handleCreateWidget = async (data: CreateWidgetSchema) => {
    try {
      // Use pending position if available (from drag/drop)
      const widgetData = pendingPosition
        ? {
            ...data,
            position_x: pendingPosition.x,
            position_y: pendingPosition.y,
            size_w: pendingPosition.w,
            size_h: pendingPosition.h,
          }
        : data;

      await createWidgetMutation.mutateAsync({
        actionGroup: ActionGroupType.widget_actions,
        data: {
          action: 'widget_actions__create',
          data: widgetData,
        },
      });
      toast.success('Widget created successfully');
      setCreateFormOpen(false);
      setPrefilledType(null);
      setPendingPosition(null);
      // Invalidate queries to refresh dashboard
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });
      onUpdate();
    } catch (error) {
      console.error('Failed to create widget:', error);
      toast.error('Failed to create widget');
    }
  };

  const handleLayoutChange = useCallback(
    (layouts: Layouts) => {
      if (!isEditMode) return;
      // Store the layout changes in state, don't save yet
      setPendingLayout(layouts);
    },
    [isEditMode]
  );

  const handleSaveLayout = useCallback(async () => {
    if (!pendingLayout) return;

    const desktopLayout = pendingLayout.lg || [];

    // Don't save if there are no widgets
    if (desktopLayout.length === 0) return;

    // Build layout array (no size constraints, just positions)
    const layoutData = desktopLayout.map((item) => ({
      i: item.i,
      x: item.x,
      y: item.y,
      w: item.w,
      h: item.h,
    }));

    try {
      await updateDashboardMutation.mutateAsync({
        actionGroup: ActionGroupType.dashboard_actions,
        objectId: dashboard.id,
        data: {
          action: 'dashboard_actions__update',
          data: {
            name: dashboard.name,
            is_default: dashboard.is_default,
            config: {
              ...dashboard.config,
              layout: layoutData,
            },
          },
        },
      });
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });
      setPendingLayout(null);
    } catch (error) {
      console.error('Failed to update widget layout:', error);
      toast.error('Failed to save widget layout');
      onUpdate();
    }
  }, [
    pendingLayout,
    dashboard.config,
    dashboard.id,
    dashboard.name,
    dashboard.is_default,
    updateDashboardMutation,
    queryClient,
    onUpdate,
  ]);

  const handleFinishEditing = useCallback(async () => {
    // Save layout if there are pending changes
    if (pendingLayout) {
      await handleSaveLayout();
    }
    // Close edit mode
    if (onCloseEditMode) {
      onCloseEditMode();
    }
  }, [pendingLayout, handleSaveLayout, onCloseEditMode]);

  // Register the finish editing handler with the parent component
  useEffect(() => {
    if (onRegisterFinishHandler) {
      onRegisterFinishHandler(handleFinishEditing);
    }
  }, [handleFinishEditing, onRegisterFinishHandler]);

  return (
    <div className="relative min-h-screen">
      {/* Grid-based layout replaces DashboardEditMode */}
      <div className={cn('relative min-h-screen', isEditMode && 'pb-96')}>
        <div className="relative z-10 min-h-screen">
          {
            <DashboardGrid
              dashboard={dashboard}
              widgets={widgets}
              isEditMode={isEditMode}
              onLayoutChange={handleLayoutChange}
              onUpdate={onUpdate}
              draggingWidgetType={draggingWidgetType}
              onWidgetDrop={handleWidgetDropOnGrid}
            />
          }
        </div>
      </div>

      {/* Widget palette - bottom horizontal sheet */}
      {isEditMode && (
        <DashboardWidgetPalette
          onWidgetClick={handleWidgetClick}
          onWidgetDragStart={handleWidgetDragStart}
          onWidgetDragEnd={handleWidgetDragEnd}
          onCloseEditMode={handleFinishEditing}
        />
      )}

      <CreateWidgetForm
        isOpen={createFormOpen}
        onOpenChange={(open) => {
          if (!open) {
            setCreateFormOpen(false);
            setPrefilledType(null);
            setPendingPosition(null);
          }
        }}
        dashboardId={dashboard.id as string}
        prefilledType={prefilledType ?? undefined}
        onSubmit={handleCreateWidget}
        isSubmitting={createWidgetMutation.isPending}
        actionLabel="Add Widget"
      />
    </div>
  );
}
