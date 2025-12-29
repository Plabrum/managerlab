import { useState, useCallback, useRef } from 'react';
import { CheckIcon, PlusCircleIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { WidgetPalette } from './widget-palette';
import type { WidgetType } from '@/types/dashboard';

interface DashboardWidgetPaletteProps {
  onWidgetClick: (widgetType: WidgetType) => void;
  onWidgetDragStart: (widgetType: WidgetType) => void;
  onWidgetDragEnd: () => void;
  onCloseEditMode?: () => void;
}

/**
 * Bottom-docked widget palette with hover-to-expand behavior
 */
export function DashboardWidgetPalette({
  onWidgetClick,
  onWidgetDragStart,
  onWidgetDragEnd,
  onCloseEditMode,
}: DashboardWidgetPaletteProps) {
  const [isPaletteHovered, setIsPaletteHovered] = useState(false);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const isPaletteExpanded = isPaletteHovered;

  const handlePaletteMouseEnter = useCallback(() => {
    // Clear any pending collapse timeout
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
      hoverTimeoutRef.current = null;
    }
    setIsPaletteHovered(true);
  }, []);

  const handlePaletteMouseLeave = useCallback(() => {
    // Small delay before collapsing to prevent flickering
    hoverTimeoutRef.current = setTimeout(() => {
      setIsPaletteHovered(false);
    }, 150);
  }, []);

  return (
    <div
      onMouseEnter={handlePaletteMouseEnter}
      onMouseLeave={handlePaletteMouseLeave}
      className={cn(
        'bg-background sticky bottom-0 left-0 right-0 z-40 flex flex-col border-t shadow-lg transition-all duration-300 ease-in-out',
        isPaletteExpanded ? 'h-80' : 'h-16'
      )}
    >
      <div className="flex h-16 shrink-0 items-center justify-between border-b px-6">
        <div className="flex items-center gap-2">
          <PlusCircleIcon className="text-muted-foreground size-5" />
          <h2 className="font-semibold">Add Widgets</h2>
          {/* Desktop expanded: show subtitle */}
          {isPaletteExpanded && (
            <span className="text-muted-foreground hidden text-sm md:block">
              Drag a widget onto the dashboard or click to configure
            </span>
          )}
        </div>
        {onCloseEditMode && (
          <Button onClick={onCloseEditMode} variant="default" size="sm">
            {/* Mobile: "Finish" */}
            <span className="md:hidden">Finish</span>
            {/* Desktop: "Finish editing" with icon */}
            <span className="hidden md:flex md:items-center">
              <CheckIcon className="mr-2 size-4" />
              Finish editing
            </span>
          </Button>
        )}
      </div>
      {isPaletteExpanded && (
        <div className="flex-1 overflow-x-auto overflow-y-hidden">
          <div className="flex gap-4 p-6">
            <WidgetPalette
              onWidgetClick={onWidgetClick}
              onWidgetDragStart={onWidgetDragStart}
              onWidgetDragEnd={onWidgetDragEnd}
            />
          </div>
        </div>
      )}
    </div>
  );
}
