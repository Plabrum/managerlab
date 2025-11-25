'use client';

import { useState, useCallback } from 'react';
import { toast } from 'sonner';
import { useQueryClient } from '@tanstack/react-query';
import { DashboardGrid } from './dashboard-grid';
import { DashboardWidgetPalette } from './dashboard-widget-palette';
import { CreateWidgetForm } from './create-widget-form';
import { widgetRegistry } from '@/lib/widgets/registry';
import { useActionsActionGroupExecuteAction } from '@/openapi/actions/actions';
import {
  ActionGroupType,
  type CreateWidgetSchema,
  type DashboardSchema,
  type ReorderWidgetsSchema,
} from '@/openapi/ariveAPI.schemas';
import type { WidgetType } from '@/types/dashboard';
import type { Layouts } from 'react-grid-layout';
import { cn } from '@/lib/utils';

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
  const [draggingWidgetType, setDraggingWidgetType] =
    useState<WidgetType | null>(null);

  // Use widgets from the new relationship
  const widgets = dashboard.widgets || [];

  // Mutations for widget operations
  const createWidgetMutation = useActionsActionGroupExecuteAction();
  const reorderWidgetsMutation = useActionsActionGroupExecuteAction();

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
    async (layout: { x: number; y: number; w: number; h: number }) => {
      if (!draggingWidgetType) return;

      const widgetEntry = widgetRegistry[draggingWidgetType];
      const defaultQuery = widgetEntry.defaults.query;

      const createData: CreateWidgetSchema = {
        dashboard_id: dashboard.id as string,
        type: draggingWidgetType,
        title: widgetEntry.metadata.name,
        description: widgetEntry.metadata.description,
        query: defaultQuery,
        position_x: layout.x,
        position_y: layout.y,
        size_w: layout.w,
        size_h: layout.h,
      };

      try {
        await createWidgetMutation.mutateAsync({
          actionGroup: ActionGroupType.widget_actions,
          data: {
            action: 'widget_actions__create',
            data: createData,
          },
        });
        toast.success('Widget created successfully');
        queryClient.invalidateQueries({ queryKey: ['dashboards'] });
        onUpdate();
      } catch (error) {
        console.error('Failed to create widget:', error);
        toast.error('Failed to create widget');
      } finally {
        setDraggingWidgetType(null);
      }
    },
    [
      draggingWidgetType,
      dashboard.id,
      createWidgetMutation,
      queryClient,
      onUpdate,
    ]
  );

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

  const handleLayoutChange = useCallback(
    async (layouts: Layouts) => {
      if (!isEditMode) return;

      const desktopLayout = layouts.lg || [];

      const reorderData: ReorderWidgetsSchema = {
        dashboard_id: dashboard.id as string,
        widgets: desktopLayout.map((item) => ({
          id: item.i,
          position_x: item.x,
          position_y: item.y,
          size_w: item.w,
          size_h: item.h,
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
        queryClient.invalidateQueries({ queryKey: ['dashboards'] });
      } catch (error) {
        console.error('Failed to update widget layout:', error);
        toast.error('Failed to save widget layout');
        onUpdate();
      }
    },
    [isEditMode, dashboard.id, reorderWidgetsMutation, queryClient, onUpdate]
  );

  return (
    <div className="relative min-h-screen">
      {/* Grid-based layout replaces DashboardEditMode */}
      <div className={cn('relative min-h-screen', isEditMode && 'pb-96')}>
        <div className="relative z-10 min-h-screen">
          {widgets.length === 0 ? (
            <div className="container mx-auto">
              <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed py-12">
                <p className="text-muted-foreground">
                  {isEditMode
                    ? 'Drag a widget from the sidebar or click to add it to your dashboard'
                    : 'No widgets configured. Click customize to add widgets.'}
                </p>
              </div>
            </div>
          ) : (
            <DashboardGrid
              widgets={widgets}
              isEditMode={isEditMode}
              onLayoutChange={handleLayoutChange}
              onUpdate={onUpdate}
              draggingWidgetType={draggingWidgetType}
              onWidgetDrop={handleWidgetDropOnGrid}
            />
          )}
        </div>
      </div>

      {/* Widget palette - bottom horizontal sheet */}
      {isEditMode && (
        <DashboardWidgetPalette
          onWidgetClick={handleWidgetClick}
          onWidgetDragStart={handleWidgetDragStart}
          onWidgetDragEnd={handleWidgetDragEnd}
          onCloseEditMode={onCloseEditMode}
        />
      )}

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
    </div>
  );
}
