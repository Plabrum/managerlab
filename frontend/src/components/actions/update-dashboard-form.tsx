'use client';

import { createTypedForm } from '@/components/forms/base';
import type { UpdateDashboardSchema } from '@/openapi/ariveAPI.schemas';

const { FormModal, FormString } = createTypedForm<UpdateDashboardSchema>();

interface UpdateDashboardFormProps {
  isOpen: boolean;
  onClose: () => void;
  defaultValues?: Partial<UpdateDashboardSchema>;
  onSubmit: (data: UpdateDashboardSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for updating a dashboard
 */
export function UpdateDashboardForm({
  isOpen,
  onClose,
  defaultValues,
  onSubmit,
  isSubmitting,
  actionLabel,
}: UpdateDashboardFormProps) {
  return (
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Update the dashboard name"
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Update Dashboard"
    >
      <FormString
        name="name"
        label="Dashboard Name"
        placeholder="My Dashboard"
      />
    </FormModal>
  );
}
