'use client';

import { useState } from 'react';
import { AddMediaToDeliverableSchema } from '@/openapi/managerLab.schemas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SelectExistingMediaForm } from './select-existing-media-form';
import { UploadNewMediaForm } from './upload-new-media-form';
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
import { useIsMobile } from '@/hooks/use-mobile';

interface AddMediaToDeliverableFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: AddMediaToDeliverableSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Wrapper component for adding media to a deliverable
 * Provides tabs to switch between selecting existing media or uploading new media
 */
export function AddMediaToDeliverableForm({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  actionLabel,
}: AddMediaToDeliverableFormProps) {
  const isMobile = useIsMobile();
  const [activeTab, setActiveTab] = useState<'select' | 'upload'>('select');

  const content = (
    <Tabs
      value={activeTab}
      onValueChange={(v) => setActiveTab(v as 'select' | 'upload')}
    >
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="select">Select Existing</TabsTrigger>
        <TabsTrigger value="upload">Upload New</TabsTrigger>
      </TabsList>

      <TabsContent value="select" className="space-y-4">
        <SelectExistingMediaForm
          onSubmit={onSubmit}
          onCancel={onClose}
          isSubmitting={isSubmitting}
        />
      </TabsContent>

      <TabsContent value="upload" className="space-y-4">
        <UploadNewMediaForm
          onSubmit={onSubmit}
          onCancel={onClose}
          isSubmitting={isSubmitting}
        />
      </TabsContent>
    </Tabs>
  );

  // Desktop: Dialog
  if (!isMobile) {
    return (
      <Dialog
        open={isOpen}
        onOpenChange={(open) => !open && !isSubmitting && onClose()}
      >
        <DialogContent className="max-w-6xl">
          <DialogHeader>
            <DialogTitle>{actionLabel}</DialogTitle>
            <DialogDescription>
              Select an existing media file or upload a new one.
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 max-h-[calc(100vh-200px)] overflow-y-auto pr-2">
            {content}
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  // Mobile: Drawer
  return (
    <Drawer
      open={isOpen}
      onOpenChange={(open) => !open && !isSubmitting && onClose()}
    >
      <DrawerContent className="max-h-[90vh]">
        <DrawerHeader className="text-left">
          <DrawerTitle>{actionLabel}</DrawerTitle>
          <DrawerDescription>
            Select an existing media file or upload a new one.
          </DrawerDescription>
        </DrawerHeader>
        <div className="overflow-y-auto px-4 pb-4">{content}</div>
      </DrawerContent>
    </Drawer>
  );
}
