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
        name="tone_of_voice"
        label="Tone of Voice"
        placeholder="Describe the brand's communication style..."
        rows={2}
      />

      <FormText
        name="brand_values"
        label="Brand Values"
        placeholder="Core values and principles..."
        rows={2}
      />

      <FormText
        name="target_audience"
        label="Target Audience"
        placeholder="Describe the target audience..."
        rows={2}
      />

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
