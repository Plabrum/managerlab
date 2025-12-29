import { createTypedForm } from '@/components/forms/base';
import type { BrandUpdateSchema } from '@/openapi/ariveAPI.schemas';

const { FormModal, FormString, FormText } =
  createTypedForm<BrandUpdateSchema>();

interface UpdateBrandFormProps {
  isOpen: boolean;
  onClose: () => void;
  defaultValues?: Partial<BrandUpdateSchema>;
  onSubmit: (data: BrandUpdateSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for updating a brand
 */
export function UpdateBrandForm({
  isOpen,
  onClose,
  defaultValues,
  onSubmit,
  isSubmitting,
  actionLabel,
}: UpdateBrandFormProps) {
  return (
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Update the brand information below."
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Update Brand"
    >
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
    </FormModal>
  );
}
