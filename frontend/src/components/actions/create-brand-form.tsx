'use client';

import { createTypedForm } from '@/components/forms/base';
import type { BrandCreateSchema } from '@/openapi/ariveAPI.schemas';

const { FormModal, FormString, FormText, FormEmail } =
  createTypedForm<BrandCreateSchema>();

interface CreateBrandFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: BrandCreateSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for creating a new brand
 */
export function CreateBrandForm({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  actionLabel,
}: CreateBrandFormProps) {
  return (
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Fill out the form below to create a new brand."
      onSubmit={onSubmit}
      isSubmitting={isSubmitting}
      submitText="Create Brand"
    >
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
    </FormModal>
  );
}
