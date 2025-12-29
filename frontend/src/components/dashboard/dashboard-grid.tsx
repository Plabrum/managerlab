import { useMemo, useCallback } from 'react';
import {
  Responsive,
  WidthProvider,
  type Layout,
  type Layouts,
} from 'react-grid-layout';
import { WidgetContainer } from './widget-container';
import { WidgetDataLoader } from './widget-data-loader';
import {
  GRID_BREAKPOINTS,
  GRID_COLS,
  buildResponsiveLayouts,
} from '@/lib/dashboard/grid-config';
import { widgetRegistry } from '@/lib/widgets/registry';
import type { WidgetSchema, DashboardSchema } from '@/openapi/ariveAPI.schemas';
import type { WidgetType, WidgetQuery } from '@/types/dashboard';
import 'react-grid-layout/css/styles.css';
import '@/styles/react-grid-layout.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

interface DashboardGridProps {
  dashboard: DashboardSchema;
  widgets: WidgetSchema[];
  isEditMode: boolean;
  onLayoutChange: (layouts: Layouts) => void;
  onUpdate: () => void;
  draggingWidgetType: WidgetType | null;
  onWidgetDrop: (layout: {
    x: number;
    y: number;
    w: number;
    h: number;
  }) => void;
}

export function DashboardGrid({
  dashboard,
  widgets,
  isEditMode,
  onLayoutChange,
  onUpdate,
  draggingWidgetType,
  onWidgetDrop,
}: DashboardGridProps) {
  const layouts = useMemo(() => {
    return buildResponsiveLayouts(widgets, dashboard);
  }, [widgets, dashboard]);

  const droppingItem = useMemo(() => {
    if (!draggingWidgetType) return undefined;

    const constraints = widgetRegistry[draggingWidgetType].sizeConstraints;
    return {
      i: '__dropping-elem__',
      w: constraints.defaultW,
      h: constraints.defaultH,
    };
  }, [draggingWidgetType]);

  const handleLayoutChange = useCallback(
    (currentLayout: Layout[], allLayouts: Layouts) => {
      if (!isEditMode) return;
      onLayoutChange(allLayouts);
    },
    [isEditMode, onLayoutChange]
  );

  const handleDrop = useCallback(
    (layout: Layout[], layoutItem: Layout) => {
      // layoutItem contains the final position where the item was dropped
      onWidgetDrop({
        x: layoutItem.x,
        y: layoutItem.y,
        w: layoutItem.w,
        h: layoutItem.h,
      });
    },
    [onWidgetDrop]
  );

  const renderWidget = (widget: WidgetSchema) => {
    const entry = widgetRegistry[widget.type as WidgetType];
    if (!entry) return <div>Unknown widget type</div>;
    const Component = entry.component;

    // Kanban widgets don't use time series data, they fetch object list data directly
    if (widget.type === 'kanban') {
      return (
        <WidgetDataLoader query={widget.query as unknown as WidgetQuery}>
          {(data) => (
            <Component
              data={data}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              {...({ query: widget.query } as any)}
            />
          )}
        </WidgetDataLoader>
      );
    }

    return (
      <WidgetDataLoader query={widget.query as unknown as WidgetQuery}>
        {(data) => <Component data={data} />}
      </WidgetDataLoader>
    );
  };

  return (
    <ResponsiveGridLayout
      className={isEditMode ? 'layout edit-mode' : 'layout'}
      layouts={layouts}
      breakpoints={GRID_BREAKPOINTS}
      cols={GRID_COLS}
      rowHeight={100}
      isDraggable={isEditMode}
      isResizable={isEditMode}
      isDroppable={isEditMode}
      draggableHandle=".widget-drag-handle"
      onLayoutChange={handleLayoutChange}
      onDrop={handleDrop}
      droppingItem={droppingItem}
      compactType={null}
      preventCollision={true}
      margin={[0, 0]}
      containerPadding={[0, 0]}
    >
      {widgets.map((widget) => (
        <div key={String(widget.id)} className="p-2">
          <WidgetContainer
            widget={widget}
            onRefetch={onUpdate}
            isEditMode={isEditMode}
          >
            {renderWidget(widget)}
          </WidgetContainer>
        </div>
      ))}
    </ResponsiveGridLayout>
  );
}
