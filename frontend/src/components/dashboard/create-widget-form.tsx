import { createTypedForm } from '@/components/forms/base';
import { type CreateWidgetSchema } from '@/openapi/ariveAPI.schemas';
import { WidgetFormFields } from './widget-form';

const { FormModal } = createTypedForm<CreateWidgetSchema>();

interface CreateWidgetFormProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  dashboardId: string;
  prefilledType?: string;
  onSubmit: (data: CreateWidgetSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for creating a new widget
 */
export function CreateWidgetForm({
  isOpen,
  onOpenChange,
  dashboardId,
  prefilledType,
  onSubmit,
  isSubmitting,
  actionLabel,
}: CreateWidgetFormProps) {
  const handleClose = () => onOpenChange(false);

  const defaultValues: Partial<CreateWidgetSchema> = {
    dashboard_id: dashboardId,
    type: prefilledType,
    title: '',
    description: '',
    position_x: 0,
    position_y: 0,
    size_w: 1,
    size_h: 1,
  };

  return (
    <FormModal
      isOpen={isOpen}
      onClose={handleClose}
      title={actionLabel}
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Add Widget"
    >
      <WidgetFormFields prefilledType={prefilledType} showTypeField={true} />
    </FormModal>
  );
}
