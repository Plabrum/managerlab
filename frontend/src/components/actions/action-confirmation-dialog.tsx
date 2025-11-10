'use client';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import type { ActionDTO } from '@/openapi/ariveAPI.schemas';

interface ActionConfirmationDialogProps {
  open: boolean;
  action: ActionDTO | null;
  isExecuting: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ActionConfirmationDialog({
  open,
  action,
  isExecuting,
  onConfirm,
  onCancel,
}: ActionConfirmationDialogProps) {
  if (!action) return null;

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onCancel()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{action.label}</DialogTitle>
          <DialogDescription>
            {action.confirmation_message || 'Are you sure you want to proceed?'}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel} disabled={isExecuting}>
            Cancel
          </Button>
          <Button
            onClick={onConfirm}
            disabled={isExecuting}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {isExecuting ? 'Executing...' : 'Confirm'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
