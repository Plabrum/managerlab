'use client';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { ActionDTO } from '@/openapi/managerLab.schemas';

interface ActionFormDialogProps {
  open: boolean;
  action: ActionDTO | null;
  isExecuting: boolean;
  onCancel: () => void;
  children: React.ReactNode;
}

/**
 * Generic wrapper for action forms that require data input
 * The actual form implementation is passed as children
 */
export function ActionFormDialog({
  open,
  action,
  isExecuting,
  onCancel,
  children,
}: ActionFormDialogProps) {
  if (!action) return null;

  return (
    <Dialog
      open={open}
      onOpenChange={(isOpen) => !isOpen && !isExecuting && onCancel()}
    >
      <DialogContent className="max-w-6xl">
        <DialogHeader>
          <DialogTitle>{action.label}</DialogTitle>
          <DialogDescription>
            Fill out the form below to complete this action.
          </DialogDescription>
        </DialogHeader>
        <div className="mt-4 max-h-[calc(100vh-200px)] overflow-y-auto pr-2">
          {children}
        </div>
      </DialogContent>
    </Dialog>
  );
}
