'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { PlusIcon } from 'lucide-react';
import { EmptyState } from '@/components/empty-state';
import { WidgetContainer } from './widget-container';
import { StatWidget } from './widgets/stat-widget';
import { BarChartWidget } from './widgets/bar-chart-widget';
import { LineChartWidget } from './widgets/line-chart-widget';
import { PieChartWidget } from './widgets/pie-chart-widget';
import { WidgetEditorDrawer } from './widget-editor-drawer';
import { dashboardsIdUpdateDashboard } from '@/openapi/dashboards/dashboards';
import type { DashboardConfig, WidgetConfig } from '@/types/dashboard';
import type { DashboardSchema } from '@/openapi/ariveAPI.schemas';
import { toast } from 'sonner';

interface DashboardWidgetsProps {
  dashboard: DashboardSchema;
  onUpdate: () => void;
}

export function DashboardWidgets({
  dashboard,
  onUpdate,
}: DashboardWidgetsProps) {
  const [editorOpen, setEditorOpen] = useState(false);
  const [editingWidget, setEditingWidget] = useState<WidgetConfig | null>(null);

  const config: DashboardConfig =
    (dashboard?.config as unknown as DashboardConfig) || { widgets: [] };

  const handleEditWidget = (widget: WidgetConfig) => {
    setEditingWidget(widget);
    setEditorOpen(true);
  };

  const handleAddWidget = () => {
    setEditingWidget(null);
    setEditorOpen(true);
  };

  const handleSaveWidget = async (widget: WidgetConfig) => {
    try {
      // Update or add widget to config
      const existingIndex = config.widgets.findIndex((w) => w.id === widget.id);
      const newWidgets = [...config.widgets];

      if (existingIndex >= 0) {
        // Update existing widget
        newWidgets[existingIndex] = widget;
      } else {
        // Add new widget - assign position in grid
        const nextPosition = calculateNextPosition(config.widgets);
        widget.position = nextPosition;
        newWidgets.push(widget);
      }

      // Update dashboard config
      await dashboardsIdUpdateDashboard(dashboard.id, {
        config: { widgets: newWidgets },
      });

      onUpdate();
      toast.success('Widget saved successfully');
    } catch (error) {
      console.error('Failed to save widget:', error);
      toast.error('Failed to save widget');
    }
  };

  const renderWidget = (widget: WidgetConfig) => {
    switch (widget.type) {
      case 'stat_number':
        return <StatWidget query={widget.query} />;
      case 'bar_chart':
        return <BarChartWidget query={widget.query} />;
      case 'line_chart':
        return <LineChartWidget query={widget.query} />;
      case 'pie_chart':
        return <PieChartWidget query={widget.query} />;
      default:
        return <div>Unknown widget type</div>;
    }
  };

  return (
    <div className="container mx-auto space-y-6 p-6">
      {/* Widgets Grid */}
      {config.widgets.length === 0 ? (
        <EmptyState
          title="Add your first widget to start visualizing your data"
          cta={{
            label: 'Add Widget',
            onClick: handleAddWidget,
          }}
          className="rounded-lg border-2 border-dashed py-12"
        />
      ) : (
        <>
          <div className="flex justify-end">
            <Button onClick={handleAddWidget}>
              <PlusIcon className="mr-2 h-4 w-4" />
              Add Widget
            </Button>
          </div>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {config.widgets.map((widget) => (
              <div key={widget.id} className="min-h-[300px]">
                <WidgetContainer widget={widget} onEdit={handleEditWidget}>
                  {renderWidget(widget)}
                </WidgetContainer>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Widget Editor Drawer */}
      <WidgetEditorDrawer
        open={editorOpen}
        onOpenChange={setEditorOpen}
        widget={editingWidget}
        onSave={handleSaveWidget}
      />
    </div>
  );
}

// Helper function to calculate next available position in grid
function calculateNextPosition(widgets: WidgetConfig[]): {
  x: number;
  y: number;
} {
  const GRID_COLS = 3;

  if (widgets.length === 0) {
    return { x: 0, y: 0 };
  }

  // Find the maximum y position
  const maxY = Math.max(...widgets.map((w) => w.position.y));

  // Count widgets in the bottom row
  const bottomRowWidgets = widgets.filter((w) => w.position.y === maxY);
  const nextX = bottomRowWidgets.length;

  if (nextX < GRID_COLS) {
    return { x: nextX, y: maxY };
  } else {
    // Start new row
    return { x: 0, y: maxY + 1 };
  }
}
