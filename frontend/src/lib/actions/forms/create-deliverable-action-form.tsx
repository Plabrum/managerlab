'use client';

import { CreateDeliverableForm } from '@/components/actions/create-deliverable-form';
import type { ActionFormProps } from '../registry';
import type { DeliverableCreateSchema } from '@/openapi/managerLab.schemas';

/**
 * Wrapper for CreateDeliverableForm that matches the registry interface
 * This adapter transforms the registry's onSubmit(data) to the action executor's format
 */
export function CreateDeliverableActionForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: ActionFormProps<DeliverableCreateSchema>) {
  return (
    <CreateDeliverableForm
      onSubmit={onSubmit}
      onCancel={onCancel}
      isSubmitting={isSubmitting}
    />
  );
}
