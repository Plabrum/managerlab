'use client';

import { useState, useCallback, useRef } from 'react';
import {
  DragDropContext,
  Droppable,
  Draggable,
  type DropResult,
} from '@hello-pangea/dnd';
import { CheckIcon, PlusCircleIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { WidgetPalette } from './widget-palette';
import { cn } from '@/lib/utils';
import type { WidgetType } from '@/lib/widgets/types';
import type { WidgetSchema } from '@/openapi/ariveAPI.schemas';

interface DashboardEditModeProps {
  isEditMode: boolean;
  widgets: WidgetSchema[];
  onWidgetDrop: (widgetType: WidgetType) => void;
  onWidgetReorder: (widgets: WidgetSchema[]) => void;
  onClose?: () => void;
  children: (props: {
    renderWidgetWrapper: (
      widget: WidgetSchema,
      index: number,
      children: React.ReactNode
    ) => React.ReactNode;
  }) => React.ReactNode;
}

export function DashboardEditMode({
  isEditMode,
  widgets,
  onWidgetDrop,
  onWidgetReorder,
  onClose,
  children,
}: DashboardEditModeProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isPaletteHovered, setIsPaletteHovered] = useState(false);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Determine if palette should be expanded
  // Expanded when: hovered (and not dragging)
  // Collapsed when: dragging OR not hovered
  const isPaletteExpanded = isPaletteHovered && !isDragging;

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

  const handleDragStart = useCallback(() => {
    setIsDragging(true);
  }, []);

  const handleDragEnd = useCallback(
    (result: DropResult) => {
      setIsDragging(false);

      const { source, destination, draggableId } = result;

      // Dropped outside any droppable area
      if (!destination) {
        return;
      }

      // Dragging from palette to dashboard
      if (
        source.droppableId === 'widget-palette' &&
        destination.droppableId === 'dashboard-widgets'
      ) {
        // Extract widget type from draggableId (e.g., "palette-bar_chart" -> "bar_chart")
        const widgetType = draggableId.replace('palette-', '') as WidgetType;
        onWidgetDrop(widgetType);
        return;
      }

      // Reordering within dashboard
      if (
        source.droppableId === 'dashboard-widgets' &&
        destination.droppableId === 'dashboard-widgets'
      ) {
        if (source.index === destination.index) {
          return;
        }

        const reorderedWidgets = Array.from(widgets);
        const [movedWidget] = reorderedWidgets.splice(source.index, 1);
        reorderedWidgets.splice(destination.index, 0, movedWidget);

        // Update positions
        const updatedWidgets = reorderedWidgets.map((widget, index) => ({
          ...widget,
          position_x: index % 3,
          position_y: Math.floor(index / 3),
        }));

        onWidgetReorder(updatedWidgets);
      }
    },
    [widgets, onWidgetDrop, onWidgetReorder]
  );

  const renderWidgetWrapper = useCallback(
    (widget: WidgetSchema, index: number, widgetChildren: React.ReactNode) => {
      const widgetId = String(widget.id);

      if (!isEditMode) {
        return (
          <div key={widgetId} className="min-h-[300px]">
            {widgetChildren}
          </div>
        );
      }

      return (
        <Draggable key={widgetId} draggableId={widgetId} index={index}>
          {(provided, snapshot) => (
            <div
              ref={provided.innerRef}
              {...provided.draggableProps}
              {...provided.dragHandleProps}
              className={cn(
                'min-h-[300px] transition-shadow',
                snapshot.isDragging && 'ring-primary/30 shadow-xl ring-2',
                isEditMode && 'cursor-grab active:cursor-grabbing'
              )}
            >
              {widgetChildren}
            </div>
          )}
        </Draggable>
      );
    },
    [isEditMode]
  );

  if (!isEditMode) {
    return (
      <div className="min-h-full p-6">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {children({ renderWidgetWrapper })}
        </div>
      </div>
    );
  }

  return (
    <DragDropContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      {/* Dashboard content area - full width with dotted grid */}
      <div
        className={cn(
          'min-h-full p-6',
          // Dotted grid background
          'bg-[radial-gradient(circle,hsl(var(--border))_1px,transparent_1px)]',
          'bg-[size:24px_24px]'
        )}
      >
        <Droppable droppableId="dashboard-widgets" direction="horizontal">
          {(provided, snapshot) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className={cn(
                'grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3',
                snapshot.isDraggingOver &&
                  'ring-primary/20 rounded-lg ring-2 ring-offset-4'
              )}
            >
              {children({ renderWidgetWrapper })}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </div>

      {/* Fixed widget palette panel on the right - overlays content */}
      <div
        onMouseEnter={handlePaletteMouseEnter}
        onMouseLeave={handlePaletteMouseLeave}
        className={cn(
          'bg-background fixed right-0 top-0 z-40 flex h-screen flex-col border-l shadow-lg transition-all duration-300 ease-in-out',
          isPaletteExpanded ? 'w-80' : 'w-16'
        )}
      >
        {/* Panel header */}
        <div className="flex h-14 shrink-0 items-center justify-center border-b px-4">
          {isPaletteExpanded ? (
            <h2 className="font-semibold">Add Widgets</h2>
          ) : (
            <PlusCircleIcon className="text-muted-foreground size-5" />
          )}
        </div>

        {/* Scrollable widget palette content */}
        <div className="flex-1 overflow-y-auto">
          <WidgetPalette collapsed={!isPaletteExpanded} />
        </div>

        {/* Finish editing button at bottom */}
        {onClose && (
          <div className="shrink-0 border-t p-3">
            {isPaletteExpanded ? (
              <Button onClick={onClose} className="w-full" variant="default">
                <CheckIcon className="mr-2 size-4" />
                Finish editing
              </Button>
            ) : (
              <Button
                onClick={onClose}
                size="icon"
                variant="default"
                className="w-full"
              >
                <CheckIcon className="size-4" />
                <span className="sr-only">Finish editing</span>
              </Button>
            )}
          </div>
        )}
      </div>
    </DragDropContext>
  );
}
