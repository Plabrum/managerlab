import type { Layouts, Layout } from 'react-grid-layout';
import type { WidgetSchema } from '@/openapi/ariveAPI.schemas';

// Grid configuration
export const GRID_CONFIG = {
  desktop: { cols: 6, rowHeight: 100, breakpoint: 768 },
  mobile: { cols: 2, rowHeight: 80 },
} as const;

export const GRID_BREAKPOINTS = { lg: 768, sm: 0 };
export const GRID_COLS = { lg: 6, sm: 2 };

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

  // Mobile: simple scaling rule
  // 1 col desktop → 1 col mobile
  // 2+ cols desktop → 2 cols mobile (full width)
  const mobileLayouts = desktopLayouts.map((item) => ({
    ...item,
    w: item.w === 1 ? 1 : 2,
    minW: Math.min(item.minW || 1, 2),
    maxW: 2,
  }));

  return { lg: desktopLayouts, sm: mobileLayouts };
}
