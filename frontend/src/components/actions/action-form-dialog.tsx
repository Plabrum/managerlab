'use client';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from '@/components/ui/drawer';
import type { ActionDTO } from '@/openapi/managerLab.schemas';
import { useIsMobile } from '@/hooks/use-mobile';

interface ActionFormDialogProps {
  open: boolean;
  action: ActionDTO | null;
  isExecuting: boolean;
  onCancel: () => void;
  children: React.ReactNode;
}

/**
 * Generic responsive wrapper for action forms that require data input
 * Automatically switches between Dialog (desktop) and Drawer (mobile)
 * The actual form implementation (with buttons) is passed as children
 */
export function ActionFormDialog({
  open,
  action,
  isExecuting,
  onCancel,
  children,
}: ActionFormDialogProps) {
  const isMobile = useIsMobile();

  if (!action) return null;

  // Desktop: Dialog
  if (!isMobile) {
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

  // Mobile: Drawer
  return (
    <Drawer
      open={open}
      onOpenChange={(isOpen) => !isOpen && !isExecuting && onCancel()}
    >
      <DrawerContent className="max-h-[90vh]">
        <DrawerHeader className="text-left">
          <DrawerTitle>{action.label}</DrawerTitle>
          <DrawerDescription>
            Fill out the form below to complete this action.
          </DrawerDescription>
        </DrawerHeader>
        <div className="overflow-y-auto px-4 pb-4">{children}</div>
      </DrawerContent>
    </Drawer>
  );
}
