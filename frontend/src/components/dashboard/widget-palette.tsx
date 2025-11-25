'use client';

import { Draggable, Droppable } from '@hello-pangea/dnd';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { widgetRegistry, getAllWidgetTypes } from '@/lib/widgets/registry';
import type { WidgetType } from '@/lib/widgets/types';
import { cn } from '@/lib/utils';

interface WidgetPaletteProps {
  collapsed?: boolean;
}

export function WidgetPalette({ collapsed = false }: WidgetPaletteProps) {
  const widgetTypes = getAllWidgetTypes();

  return (
    <div className="flex flex-col gap-3 p-4">
      <Droppable droppableId="widget-palette" isDropDisabled={true}>
        {(provided) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className="flex flex-col gap-3"
          >
            {widgetTypes.map((type, index) => (
              <DraggableWidgetCard
                key={type}
                widgetType={type}
                index={index}
                collapsed={collapsed}
              />
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  );
}

interface DraggableWidgetCardProps {
  widgetType: WidgetType;
  index: number;
  collapsed?: boolean;
}

function DraggableWidgetCard({
  widgetType,
  index,
  collapsed = false,
}: DraggableWidgetCardProps) {
  const entry = widgetRegistry[widgetType];
  const { metadata, preview: Preview } = entry;
  const Icon = metadata.icon;

  return (
    <Draggable draggableId={`palette-${widgetType}`} index={index}>
      {(provided, snapshot) => (
        <Card
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={cn(
            'cursor-grab transition-shadow active:cursor-grabbing',
            snapshot.isDragging && 'ring-primary/20 shadow-lg ring-2',
            collapsed && 'p-2'
          )}
        >
          {collapsed ? (
            <div className="flex items-center justify-center">
              <Icon className="text-muted-foreground h-5 w-5" />
            </div>
          ) : (
            <>
              <CardHeader className="p-3 pb-0">
                <div className="flex items-center gap-2">
                  <Icon className="text-muted-foreground h-4 w-4" />
                  <CardTitle className="text-sm">{metadata.name}</CardTitle>
                </div>
                <CardDescription className="text-xs">
                  {metadata.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="p-3 pt-2">
                <div className="bg-muted/30 pointer-events-none rounded border p-2">
                  <Preview />
                </div>
              </CardContent>
            </>
          )}
        </Card>
      )}
    </Draggable>
  );
}
