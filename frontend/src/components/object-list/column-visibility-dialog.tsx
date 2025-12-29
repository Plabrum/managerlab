import type { VisibilityState } from '@tanstack/react-table';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import type { ColumnDefinitionSchema } from '@/openapi/ariveAPI.schemas';

interface ColumnVisibilityDialogProps {
  columns: ColumnDefinitionSchema[];
  columnVisibility: VisibilityState;
  onColumnVisibilityChange: (visibility: VisibilityState) => void;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ColumnVisibilityDialog({
  columns,
  columnVisibility,
  onColumnVisibilityChange,
  open,
  onOpenChange,
}: ColumnVisibilityDialogProps) {
  // Count visible columns
  const visibleCount = columns.filter(
    (col) => columnVisibility[col.key] ?? true
  ).length;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Manage Columns</DialogTitle>
          <DialogDescription>
            Show or hide columns in the table ({visibleCount} of{' '}
            {columns.length} visible)
          </DialogDescription>
        </DialogHeader>
        <div className="max-h-96 space-y-3 overflow-y-auto py-4">
          {columns.map((col) => (
            <div key={col.key} className="flex items-center space-x-3">
              <Checkbox
                id={`col-${col.key}`}
                checked={columnVisibility[col.key] ?? true}
                onCheckedChange={(checked) => {
                  onColumnVisibilityChange({
                    ...columnVisibility,
                    [col.key]: !!checked,
                  });
                }}
              />
              <Label
                htmlFor={`col-${col.key}`}
                className="flex-1 cursor-pointer text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                {col.label || col.key}
              </Label>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
