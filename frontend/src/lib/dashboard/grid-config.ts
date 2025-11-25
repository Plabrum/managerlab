import type { Layouts, Layout } from 'react-grid-layout';
import type { WidgetSchema } from '@/openapi/ariveAPI.schemas';

// Grid configuration
export const GRID_CONFIG = {
  desktop: { cols: 6, rowHeight: 100, breakpoint: 768 },
  mobile: { cols: 3, rowHeight: 80 },
} as const;

export const GRID_BREAKPOINTS = { lg: 768, sm: 0 };
export const GRID_COLS = { lg: 6, sm: 3 };

/**
 * Convert widget to react-grid-layout item
 */
export function widgetToGridItem(widget: WidgetSchema): Layout {
  return {
    i: String(widget.id),
    x: widget.position_x,
    y: widget.position_y,
    w: widget.size_w,
    h: widget.size_h,
  };
}

/**
 * Convert grid item back to widget position/size update
 */
export function gridItemToWidgetUpdate(item: Layout) {
  return {
    id: item.i,
    position_x: item.x,
    position_y: item.y,
    size_w: item.w,
    size_h: item.h,
  };
}

/**
 * Build responsive layouts for react-grid-layout
 */
export function buildResponsiveLayouts(widgets: WidgetSchema[]): Layouts {
  const desktopLayouts = widgets.map(widgetToGridItem);

  // Mobile: scale to fit 3 columns
  const mobileLayouts = desktopLayouts.map((item) => ({
    ...item,
    w: Math.min(Math.ceil(item.w / 2), 3), // 6 cols → 3 cols
    minW: Math.min(item.minW || 1, 3),
    maxW: 3,
  }));

  return { lg: desktopLayouts, sm: mobileLayouts };
}
