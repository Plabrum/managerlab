import { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { widgetRegistry, getAllWidgetTypes } from '@/lib/widgets/registry';
import type { WidgetType } from '@/lib/widgets/types';

interface WidgetPaletteProps {
  onWidgetClick: (widgetType: WidgetType) => void;
  onWidgetDragStart: (widgetType: WidgetType) => void;
  onWidgetDragEnd: () => void;
}

export function WidgetPalette({
  onWidgetClick,
  onWidgetDragStart,
  onWidgetDragEnd,
}: WidgetPaletteProps) {
  const widgetTypes = getAllWidgetTypes();

  return (
    <div className="flex gap-4">
      {widgetTypes.map((type) => (
        <DraggableWidgetCard
          key={type}
          widgetType={type}
          onWidgetClick={onWidgetClick}
          onWidgetDragStart={onWidgetDragStart}
          onWidgetDragEnd={onWidgetDragEnd}
        />
      ))}
    </div>
  );
}

interface DraggableWidgetCardProps {
  widgetType: WidgetType;
  onWidgetClick: (widgetType: WidgetType) => void;
  onWidgetDragStart: (widgetType: WidgetType) => void;
  onWidgetDragEnd: () => void;
}

function DraggableWidgetCard({
  widgetType,
  onWidgetClick,
  onWidgetDragStart,
  onWidgetDragEnd,
}: DraggableWidgetCardProps) {
  const entry = widgetRegistry[widgetType];
  const { metadata, preview: Preview } = entry;
  const Icon = metadata.icon;
  const [isDragging, setIsDragging] = useState(false);

  // Use native HTML5 drag for react-grid-layout compatibility
  const handleDragStart = (e: React.DragEvent<HTMLDivElement>) => {
    setIsDragging(true);
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('text/plain', '');

    // Create a custom drag image from the card element
    const dragImage = e.currentTarget.cloneNode(true) as HTMLElement;
    dragImage.style.width = `${e.currentTarget.offsetWidth}px`;
    dragImage.style.position = 'absolute';
    dragImage.style.top = '-9999px';
    dragImage.style.opacity = '0.8';
    document.body.appendChild(dragImage);

    e.dataTransfer.setDragImage(dragImage, e.currentTarget.offsetWidth / 2, 20);

    // Clean up after a short delay
    setTimeout(() => {
      document.body.removeChild(dragImage);
    }, 0);

    onWidgetDragStart(widgetType);
  };

  const handleDragEnd = () => {
    setIsDragging(false);
    onWidgetDragEnd();
  };

  return (
    <Card
      draggable
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onClick={() => onWidgetClick(widgetType)}
      className={cn(
        'w-64 shrink-0 cursor-grab transition-all active:cursor-grabbing',
        isDragging && 'ring-primary/20 opacity-50 shadow-lg ring-2'
      )}
    >
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
    </Card>
  );
}
