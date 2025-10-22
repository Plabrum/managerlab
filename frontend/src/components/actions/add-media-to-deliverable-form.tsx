'use client';

import { useState } from 'react';
import { AddMediaToDeliverableSchema } from '@/openapi/managerLab.schemas';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SelectExistingMediaForm } from './select-existing-media-form';
import { UploadNewMediaForm } from './upload-new-media-form';

interface AddMediaToDeliverableFormProps {
  onSubmit: (data: AddMediaToDeliverableSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Wrapper component for adding media to a deliverable
 * Provides tabs to switch between selecting existing media or uploading new media
 */
export function AddMediaToDeliverableForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: AddMediaToDeliverableFormProps) {
  const [activeTab, setActiveTab] = useState<'select' | 'upload'>('select');

  return (
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
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      </TabsContent>

      <TabsContent value="upload" className="space-y-4">
        <UploadNewMediaForm
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      </TabsContent>
    </Tabs>
  );
}
