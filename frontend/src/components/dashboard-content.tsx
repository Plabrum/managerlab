'use client';

import { useEffect, useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { PlusIcon } from 'lucide-react';
import { EmptyState } from '@/components/empty-state';
import { WidgetContainer } from './dashboard/widget-container';
import { StatWidget } from './dashboard/widgets/stat-widget';
import { BarChartWidget } from './dashboard/widgets/bar-chart-widget';
import { LineChartWidget } from './dashboard/widgets/line-chart-widget';
import { PieChartWidget } from './dashboard/widgets/pie-chart-widget';
import { WidgetEditorDrawer } from './dashboard/widget-editor-drawer';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  dashboardsListDashboards,
  dashboardsIdUpdateDashboard,
  dashboardsCreateDashboard,
  dashboardsIdGetDashboard,
} from '@/openapi/dashboards/dashboards';
import type { DashboardConfig, WidgetConfig } from '@/types/dashboard';
import type { DashboardSchema } from '@/openapi/ariveAPI.schemas';
import { toast } from 'sonner';
import { PageTopBar } from '@/components/page-topbar';

interface DashboardContentProps {
  dashboardId?: string;
}

export function DashboardContent({ dashboardId }: DashboardContentProps = {}) {
  const [dashboard, setDashboard] = useState<DashboardSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [editorOpen, setEditorOpen] = useState(false);
  const [editingWidget, setEditingWidget] = useState<WidgetConfig | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newDashboardName, setNewDashboardName] = useState('');
  const [creating, setCreating] = useState(false);

  const fetchDashboards = useCallback(async () => {
    try {
      setLoading(true);

      if (dashboardId) {
        // Fetch specific dashboard by ID
        const specificDashboard = await dashboardsIdGetDashboard(dashboardId);
        setDashboard(specificDashboard);
      } else {
        // Fetch all dashboards and get the default or first one
        const dashboards = await dashboardsListDashboards();
        const defaultDashboard =
          dashboards.find((d) => d.is_default) || dashboards[0];
        setDashboard(defaultDashboard || null);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
      toast.error('Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  }, [dashboardId]);

  useEffect(() => {
    fetchDashboards();
  }, [fetchDashboards]);

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

  const handleCreateDashboard = async () => {
    if (!newDashboardName.trim()) {
      toast.error('Please enter a dashboard name');
      return;
    }

    try {
      setCreating(true);
      const newDashboard = await dashboardsCreateDashboard({
        name: newDashboardName,
        config: { widgets: [] },
        is_personal: true,
        is_default: false,
      });

      setDashboard(newDashboard);
      setCreateDialogOpen(false);
      setNewDashboardName('');
      toast.success('Dashboard created successfully');
    } catch (error) {
      console.error('Failed to create dashboard:', error);
      toast.error('Failed to create dashboard');
    } finally {
      setCreating(false);
    }
  };

  const handleSaveWidget = async (widget: WidgetConfig) => {
    if (!dashboard) return;

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
      const updatedDashboard = await dashboardsIdUpdateDashboard(dashboard.id, {
        config: { widgets: newWidgets },
      });

      setDashboard(updatedDashboard);
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

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-muted-foreground text-sm">
          Loading dashboard...
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <PageTopBar
        title="Dashboard"
        actions={
          <Button onClick={() => setCreateDialogOpen(true)}>
            <PlusIcon className="mr-2 h-4 w-4" />
            Create Dashboard
          </Button>
        }
      >
        <div className="container mx-auto space-y-6 p-6">
          <EmptyState
            title="Create a dashboard to get started"
            cta={{
              label: 'Create Dashboard',
              onClick: () => setCreateDialogOpen(true),
            }}
            className="rounded-lg border-2 border-dashed py-12"
          />

          {/* Create Dashboard Dialog */}
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Dashboard</DialogTitle>
                <DialogDescription>
                  Create a new dashboard to visualize your data
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="dashboard-name">Dashboard Name</Label>
                  <Input
                    id="dashboard-name"
                    placeholder="My Dashboard"
                    value={newDashboardName}
                    onChange={(e) => setNewDashboardName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleCreateDashboard();
                      }
                    }}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => {
                    setCreateDialogOpen(false);
                    setNewDashboardName('');
                  }}
                >
                  Cancel
                </Button>
                <Button onClick={handleCreateDashboard} disabled={creating}>
                  {creating ? 'Creating...' : 'Create'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </PageTopBar>
    );
  }

  return (
    <PageTopBar
      title={dashboard.name}
      actions={
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setCreateDialogOpen(true)}>
            <PlusIcon className="mr-2 h-4 w-4" />
            New Dashboard
          </Button>
          <Button onClick={handleAddWidget}>
            <PlusIcon className="mr-2 h-4 w-4" />
            Add Widget
          </Button>
        </div>
      }
    >
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
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {config.widgets.map((widget) => (
              <div key={widget.id} className="min-h-[300px]">
                <WidgetContainer widget={widget} onEdit={handleEditWidget}>
                  {renderWidget(widget)}
                </WidgetContainer>
              </div>
            ))}
          </div>
        )}

        {/* Widget Editor Drawer */}
        <WidgetEditorDrawer
          open={editorOpen}
          onOpenChange={setEditorOpen}
          widget={editingWidget}
          onSave={handleSaveWidget}
        />

        {/* Create Dashboard Dialog */}
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Dashboard</DialogTitle>
              <DialogDescription>
                Create a new dashboard to visualize your data
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="dashboard-name">Dashboard Name</Label>
                <Input
                  id="dashboard-name"
                  placeholder="My Dashboard"
                  value={newDashboardName}
                  onChange={(e) => setNewDashboardName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleCreateDashboard();
                    }
                  }}
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setCreateDialogOpen(false);
                  setNewDashboardName('');
                }}
              >
                Cancel
              </Button>
              <Button onClick={handleCreateDashboard} disabled={creating}>
                {creating ? 'Creating...' : 'Create'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </PageTopBar>
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
