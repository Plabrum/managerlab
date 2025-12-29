import { createTypedForm } from '@/components/forms/base';
import type { CreateDashboardSchema } from '@/openapi/ariveAPI.schemas';

const { FormModal, FormString, FormCustom } =
  createTypedForm<CreateDashboardSchema>();

interface CreateDashboardFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateDashboardSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for creating a new dashboard
 */
export function CreateDashboardForm({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  actionLabel,
}: CreateDashboardFormProps) {
  const handleFormSubmit = (data: CreateDashboardSchema) => {
    // Ensure config is set to empty object if not provided
    const submissionData: CreateDashboardSchema = {
      ...data,
      config: data.config ?? {},
      is_personal: data.is_personal ?? false,
      is_default: data.is_default ?? false,
    };
    onSubmit(submissionData);
  };

  return (
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Create a new dashboard to organize your widgets."
      onSubmit={handleFormSubmit}
      isSubmitting={isSubmitting}
      submitText="Create Dashboard"
    >
      <FormString
        name="name"
        label="Dashboard Name"
        placeholder="My Dashboard"
        required="Dashboard name is required"
        autoFocus
      />

      <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-sm font-medium">Dashboard Settings</h3>

        <FormCustom name="is_personal">
          {({ value, onChange }) => (
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_personal"
                checked={value as boolean}
                onChange={(e) => onChange(e.target.checked)}
                className="text-primary focus:ring-primary h-4 w-4 rounded border-gray-300 focus:ring-2"
              />
              <label
                htmlFor="is_personal"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Personal Dashboard
              </label>
            </div>
          )}
        </FormCustom>
        <p className="text-muted-foreground text-xs">
          Personal dashboards are only visible to you. Uncheck to make it
          visible to your entire team.
        </p>

        <FormCustom name="is_default">
          {({ value, onChange }) => (
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_default"
                checked={value as boolean}
                onChange={(e) => onChange(e.target.checked)}
                className="text-primary focus:ring-primary h-4 w-4 rounded border-gray-300 focus:ring-2"
              />
              <label
                htmlFor="is_default"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Set as Default Dashboard
              </label>
            </div>
          )}
        </FormCustom>
        <p className="text-muted-foreground text-xs">
          The default dashboard will be shown when you first visit the dashboard
          page.
        </p>
      </div>
    </FormModal>
  );
}
