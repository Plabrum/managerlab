'use client';

import { Button } from '@/components/ui/button';
import { createTypedForm } from '@/components/forms/base';
import type { BrandCreateSchema } from '@/openapi/managerLab.schemas';

const { Form, FormString, FormText, FormEmail } =
  createTypedForm<BrandCreateSchema>();

interface CreateBrandFormProps {
  onSubmit: (data: BrandCreateSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Form for creating a new brand
 */
export function CreateBrandForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: CreateBrandFormProps) {
  return (
    <Form onSubmit={onSubmit}>
      <FormString
        name="name"
        label="Brand Name"
        placeholder="Brand name"
        required="Brand name is required"
        autoFocus
      />

      <FormText
        name="description"
        label="Description"
        placeholder="Brand description..."
        rows={3}
      />

      <FormString
        name="website"
        label="Website"
        placeholder="https://example.com"
      />

      <FormEmail name="email" label="Email" placeholder="contact@example.com" />

      <FormString name="phone" label="Phone" placeholder="+1 (555) 000-0000" />

      <FormText
        name="notes"
        label="Notes"
        placeholder="Additional notes..."
        rows={2}
      />

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? 'Creating...' : 'Create Brand'}
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
