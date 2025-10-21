'use client';

import { UpdateDeliverableForm } from '@/components/actions/update-deliverable-form';
import type { ActionFormProps } from '../registry';
import type { DeliverableUpdateSchema } from '@/openapi/managerLab.schemas';

/**
 * Wrapper for UpdateDeliverableForm that matches the registry interface
 * This adapter transforms the registry's onSubmit(data) to the action executor's format
 */
export function UpdateDeliverableActionForm({
  defaultValues,
  onSubmit,
  onCancel,
  isSubmitting,
}: ActionFormProps<DeliverableUpdateSchema>) {
  return (
    <UpdateDeliverableForm
      defaultValues={defaultValues}
      onSubmit={(data) => {
        // The registry onSubmit receives the full action body
        onSubmit(data);
      }}
      onCancel={onCancel}
      isSubmitting={isSubmitting}
    />
  );
}
