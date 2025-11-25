'use client';

import { useMemo, useCallback } from 'react';
import {
  Responsive,
  WidthProvider,
  type Layout,
  type Layouts,
} from 'react-grid-layout';
import { WidgetContainer } from './widget-container';
import { widgetRegistry } from '@/lib/widgets/registry';
import {
  GRID_BREAKPOINTS,
  GRID_COLS,
  buildResponsiveLayouts,
} from '@/lib/dashboard/grid-config';
import type { WidgetSchema } from '@/openapi/ariveAPI.schemas';
import type { WidgetType, WidgetQuery } from '@/types/dashboard';
import 'react-grid-layout/css/styles.css';
import '@/app/react-grid-layout.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

interface DashboardGridProps {
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
  widgets,
  isEditMode,
  onLayoutChange,
  onUpdate,
  draggingWidgetType,
  onWidgetDrop,
}: DashboardGridProps) {
  const layouts = useMemo(() => {
    const baseLayouts = buildResponsiveLayouts(widgets);

    // Apply per-widget size constraints
    return {
      lg: baseLayouts.lg.map((item) => {
        const widget = widgets.find((w) => String(w.id) === item.i);
        if (!widget) return item;

        const constraints =
          widgetRegistry[widget.type as WidgetType].sizeConstraints;
        return {
          ...item,
          minW: constraints.minW,
          minH: constraints.minH,
          maxW: 6,
        };
      }),
      sm: baseLayouts.sm.map((item) => {
        const widget = widgets.find((w) => String(w.id) === item.i);
        if (!widget) return item;

        const constraints =
          widgetRegistry[widget.type as WidgetType].sizeConstraints;
        return {
          ...item,
          minW: Math.min(constraints.minW, 2),
          minH: constraints.minH,
          maxW: 2,
        };
      }),
    };
  }, [widgets]);

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
    return <Component query={widget.query as unknown as WidgetQuery} />;
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
