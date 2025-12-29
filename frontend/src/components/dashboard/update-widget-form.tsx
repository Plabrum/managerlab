import { WidgetFormFields } from './widget-form';
import { createTypedForm } from '@/components/forms/base';
import type {
  WidgetSchema,
  EditWidgetSchema,
} from '@/openapi/ariveAPI.schemas';

const { FormModal } = createTypedForm<EditWidgetSchema>();

interface UpdateWidgetFormProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  widget?: WidgetSchema;
  onSubmit: (data: EditWidgetSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for updating an existing widget
 */
export function UpdateWidgetForm({
  isOpen,
  onOpenChange,
  widget,
  onSubmit,
  isSubmitting,
  actionLabel,
}: UpdateWidgetFormProps) {
  const handleClose = () => onOpenChange(false);

  const defaultValues: Partial<EditWidgetSchema> = widget
    ? {
        type: widget.type,
        title: widget.title,
        description: widget.description ?? '',
        query: widget.query,
      }
    : {};

  return (
    <FormModal
      isOpen={isOpen}
      onClose={handleClose}
      title={actionLabel}
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Edit Widget"
    >
      <WidgetFormFields prefilledType={widget?.type} showTypeField={true} />
    </FormModal>
  );
}
