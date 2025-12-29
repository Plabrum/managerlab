import { createTypedForm } from '@/components/forms/base';
import type {
  UpdateDashboardSchema,
  DashboardSchema,
} from '@/openapi/ariveAPI.schemas';

const { FormModal, FormString } = createTypedForm<UpdateDashboardSchema>();

interface UpdateDashboardFormProps {
  isOpen: boolean;
  onClose: () => void;
  defaultValues?: Partial<DashboardSchema>;
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
  // Handler that ensures all required fields are included
  const handleSubmit = (data: UpdateDashboardSchema) => {
    // Include the existing config and is_default from defaultValues
    const completeData: UpdateDashboardSchema = {
      name: data.name,
      config: defaultValues?.config ?? {},
      is_default: defaultValues?.is_default ?? false,
    };
    onSubmit(completeData);
  };

  return (
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Update the dashboard name"
      onSubmit={handleSubmit}
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
