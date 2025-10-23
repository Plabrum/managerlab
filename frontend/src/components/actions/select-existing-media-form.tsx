'use client';

import { Button } from '@/components/ui/button';
import { createTypedForm } from '@/components/forms/base';
import { AddMediaToDeliverableSchema } from '@/openapi/managerLab.schemas';
import { useListObjects } from '@/openapi/objects/objects';
import { MediaSelector } from '@/components/media/MediaSelector';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

const { Form, FormCustom } = createTypedForm<AddMediaToDeliverableSchema>();

interface SelectExistingMediaFormProps {
  onSubmit: (data: AddMediaToDeliverableSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Form for selecting existing media to add to a deliverable
 * Simple wrapper around MediaSelector with form validation
 */
export function SelectExistingMediaForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: SelectExistingMediaFormProps) {
  // Fetch available media
  const { data: mediaList, isLoading } = useListObjects('media', {
    offset: 0,
    limit: 100,
    sorts: [],
    filters: [],
  });

  const handleFormSubmit = (data: AddMediaToDeliverableSchema) => {
    if (data.media_ids.length === 0) {
      toast.error('Please select at least one media item');
      return;
    }
    onSubmit(data);
  };

  const mediaItems = mediaList?.objects || [];

  return (
    <Form onSubmit={handleFormSubmit} defaultValues={{ media_ids: [] }}>
      <FormCustom name="media_ids">
        {({ value, onChange }) => {
          const mediaIds = value as string[];
          return (
            <MediaSelector
              items={mediaItems}
              selectedIds={mediaIds}
              onToggle={(mediaId, checked) => {
                const newValue = checked
                  ? [...mediaIds, mediaId]
                  : mediaIds.filter((id) => id !== mediaId);
                onChange(newValue);
              }}
              isLoading={isLoading}
              disabled={isSubmitting}
              emptyMessage="No media available. Try uploading new media instead."
            />
          );
        }}
      </FormCustom>

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Adding...
            </>
          ) : (
            'Add Selected Media'
          )}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isSubmitting}
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </Form>
  );
}
