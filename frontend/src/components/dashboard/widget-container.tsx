'use client';

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { WidgetEditControls } from './widget-edit-controls';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import { ActionGroupType, type WidgetSchema } from '@/openapi/ariveAPI.schemas';
import { useActionExecutor } from '@/hooks/use-action-executor';
import { useActionFormRenderer } from '@/hooks/use-action-form-renderer';

interface WidgetContainerProps {
  widget: WidgetSchema;
  onRefetch: () => void;
  children: React.ReactNode;
  isEditMode?: boolean;
}

export function WidgetContainer({
  widget,
  onRefetch,
  children,
  isEditMode = false,
}: WidgetContainerProps) {
  const actions = widget.actions ?? [];
  const editAction = actions.find((a) => a.action.endsWith('__edit'));
  const deleteAction = actions.find((a) => a.action.endsWith('__delete'));

  const formRenderer = useActionFormRenderer(widget);

  const executor = useActionExecutor({
    actionGroup: ActionGroupType.widget_actions,
    objectId: String(widget.id),
    renderActionForm: formRenderer,
    onInvalidate: onRefetch,
  });

  const handleEdit = () => {
    if (editAction) {
      executor.initiateAction(editAction);
    }
  };

  const handleDelete = () => {
    if (deleteAction) {
      executor.initiateAction(deleteAction);
    }
  };

  return (
    <Card className="relative flex h-full flex-col gap-y-0 px-4 py-6">
      {isEditMode && (
        <WidgetEditControls onEdit={handleEdit} onDelete={handleDelete} />
      )}

      <CardHeader className="space-y-0 p-0">
        <CardTitle className="text-base font-medium">{widget.title}</CardTitle>
        {widget.description && (
          <CardDescription className="text-sm">
            {widget.description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent className="flex-1 px-0">{children}</CardContent>

      <ActionConfirmationDialog
        open={executor.showConfirmation}
        action={executor.pendingAction}
        isExecuting={executor.isExecuting}
        onConfirm={executor.confirmAction}
        onCancel={executor.cancelAction}
      />

      {executor.renderActionForm &&
        executor.pendingAction &&
        executor.renderActionForm({
          action: executor.pendingAction,
          onSubmit: executor.executeWithData,
          onClose: executor.cancelAction,
          isSubmitting: executor.isExecuting,
          isOpen: executor.showForm,
          actionLabel: executor.pendingAction.label,
        })}
    </Card>
  );
}
