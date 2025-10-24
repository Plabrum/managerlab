'use client';

import { Button } from '@/components/ui/button';
import { createTypedForm } from '@/components/forms/base';
import type { BrandUpdateSchema } from '@/openapi/managerLab.schemas';

const { Form, FormString, FormText } = createTypedForm<BrandUpdateSchema>();

interface UpdateBrandFormProps {
  defaultValues?: Partial<BrandUpdateSchema>;
  onSubmit: (data: BrandUpdateSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Form for updating a brand
 */
export function UpdateBrandForm({
  defaultValues,
  onSubmit,
  onCancel,
  isSubmitting,
}: UpdateBrandFormProps) {
  return (
    <Form onSubmit={onSubmit} defaultValues={defaultValues}>
      <FormString name="name" label="Brand Name" placeholder="Brand name" />

      <FormText
        name="description"
        label="Description"
        placeholder="Brief description of the brand..."
        rows={3}
      />

      <FormString
        name="website"
        label="Website"
        type="url"
        placeholder="https://example.com"
      />

      <FormString
        name="email"
        label="Email"
        type="email"
        placeholder="contact@brand.com"
      />

      <FormText
        name="notes"
        label="Notes"
        placeholder="Additional notes..."
        rows={4}
      />

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? 'Updating...' : 'Update Brand'}
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
