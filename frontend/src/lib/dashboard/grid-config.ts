import { widgetRegistry } from '@/lib/widgets/registry';
import type { WidgetSchema, DashboardSchema } from '@/openapi/ariveAPI.schemas';
import type { WidgetType } from '@/types/dashboard';
import type { Layouts } from 'react-grid-layout';

// Grid configuration
export const GRID_CONFIG = {
  desktop: { cols: 6, rowHeight: 100, breakpoint: 768 },
  mobile: { cols: 2, rowHeight: 80 },
} as const;

export const GRID_BREAKPOINTS = { lg: 768, sm: 0 };
export const GRID_COLS = { lg: 6, sm: 2 };

/**
 * Build responsive layouts for react-grid-layout from dashboard config
 */
export function buildResponsiveLayouts(
  widgets: WidgetSchema[],
  dashboard: DashboardSchema
): Layouts {
  const configLayout = dashboard.config?.layout as
    | Array<{
        i: string;
        x: number;
        y: number;
        w: number;
        h: number;
      }>
    | undefined;

  if (configLayout && configLayout.length > 0) {
    // Use stored layout from config
    const desktopLayout = configLayout.map((item) => {
      const widget = widgets.find((w) => String(w.id) === item.i);

      // Apply size constraints from registry
      const widgetType = widget?.type as WidgetType | undefined;
      const constraints = widgetType
        ? widgetRegistry[widgetType]?.sizeConstraints
        : undefined;

      return {
        ...item,
        minW: constraints?.minW,
        minH: constraints?.minH,
        maxW: 6,
      };
    });

    // Derive mobile layout
    const mobileLayout = desktopLayout.map((item) => ({
      i: item.i,
      x: item.x,
      y: item.y,
      w: item.w === 1 ? 1 : 2,
      h: item.h,
      minW: Math.min(item.minW || 1, 2),
      minH: item.minH,
      maxW: 2,
    }));

    return { lg: desktopLayout, sm: mobileLayout };
  }

  // Fallback: build default layout (for new dashboards or missing config)
  return buildDefaultLayout(widgets);
}

/**
 * Build default stacked layout for widgets
 */
function buildDefaultLayout(widgets: WidgetSchema[]): Layouts {
  let currentY = 0;
  const desktopLayout = widgets.map((widget) => {
    const widgetType = widget.type as WidgetType;
    const constraints = widgetRegistry[widgetType]?.sizeConstraints;
    const w = constraints?.defaultW || 2;
    const h = constraints?.defaultH || 2;

    const item = {
      i: String(widget.id),
      x: 0,
      y: currentY,
      w,
      h,
      minW: constraints?.minW,
      minH: constraints?.minH,
      maxW: 6,
    };

    currentY += h;
    return item;
  });

  const mobileLayout = desktopLayout.map((item) => ({
    ...item,
    w: item.w === 1 ? 1 : 2,
    minW: Math.min(item.minW || 1, 2),
    maxW: 2,
  }));

  return { lg: desktopLayout, sm: mobileLayout };
}
