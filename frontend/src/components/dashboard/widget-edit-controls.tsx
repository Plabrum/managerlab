import { Pencil, Trash2, Maximize2 } from 'lucide-react';

interface WidgetEditControlsProps {
  onEdit: () => void;
  onDelete: () => void;
  onResize?: () => void;
}

export function WidgetEditControls({
  onEdit,
  onDelete,
  onResize,
}: WidgetEditControlsProps) {
  return (
    <>
      {/* Edit button - top right */}
      <button
        className="text-muted-foreground hover:text-foreground absolute right-2 top-2 z-10 cursor-pointer transition-colors"
        onClick={(e) => {
          e.stopPropagation();
          onEdit();
        }}
        title="Edit widget"
      >
        <Pencil className="size-4" />
      </button>

      {/* Delete button - bottom left */}
      <button
        className="text-muted-foreground hover:text-destructive absolute bottom-2 left-2 z-10 cursor-pointer transition-colors"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        title="Delete widget"
      >
        <Trash2 className="size-4" />
      </button>

      {/* Resize button - bottom right corner */}
      {onResize && (
        <button
          className="text-muted-foreground hover:text-foreground absolute bottom-2 right-2 z-10 cursor-nwse-resize transition-colors"
          onClick={(e) => {
            e.stopPropagation();
            onResize();
          }}
          title="Resize widget"
        >
          <Maximize2 className="size-4" />
        </button>
      )}
    </>
  );
}
