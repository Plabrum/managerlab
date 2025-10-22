'use client';

import { Button } from '@/components/ui/button';
import { createTypedForm } from '@/components/forms/base';
import type { DeliverableUpdateSchema } from '@/openapi/managerLab.schemas';

const { Form, FormString, FormText } =
  createTypedForm<DeliverableUpdateSchema>();

interface UpdateDeliverableFormProps {
  defaultValues?: Partial<DeliverableUpdateSchema>;
  onSubmit: (data: DeliverableUpdateSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Form for updating a deliverable
 */
export function UpdateDeliverableForm({
  defaultValues,
  onSubmit,
  onCancel,
  isSubmitting,
}: UpdateDeliverableFormProps) {
  return (
    <Form onSubmit={onSubmit} defaultValues={defaultValues}>
      <FormString name="title" label="Title" placeholder="Deliverable title" />

      <FormText
        name="content"
        label="Content"
        placeholder="Post content..."
        rows={4}
      />

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? 'Updating...' : 'Update Deliverable'}
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
