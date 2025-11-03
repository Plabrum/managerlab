'use client';

import { Button } from '@/components/ui/button';
import { Check, X } from 'lucide-react';
import type { DeliverableMediaAssociationSchema } from '@/openapi/managerLab.schemas';
import { ActionGroupType } from '@/openapi/managerLab.schemas';
import { useActionExecutor } from '@/hooks/use-action-executor';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import { ActionFormDialog } from '@/components/actions/action-form-dialog';

interface MediaApprovalActionsProps {
  mediaAssociation: DeliverableMediaAssociationSchema;
  onActionComplete?: () => void;
}

export function MediaApprovalActions({
  mediaAssociation,
  onActionComplete,
}: MediaApprovalActionsProps) {
  const executor = useActionExecutor({
    actionGroup: ActionGroupType.deliverable_media_actions,
    objectId: String(mediaAssociation.id),
    onSuccess: () => {
      onActionComplete?.();
    },
  });

  const actions = mediaAssociation.actions || [];
  const availableActions = actions.filter(
    (action) => action.available !== false
  );

  // Find specific actions by name (backend uses 'accept', 'reject')
  const acceptAction = availableActions.find((a) =>
    a.action.toLowerCase().includes('accept')
  );
  const rejectAction = availableActions.find((a) =>
    a.action.toLowerCase().includes('reject')
  );

  if (availableActions.length === 0) {
    return null;
  }

  return (
    <>
      <div className="flex items-center gap-2">
        {acceptAction && (
          <Button
            variant="default"
            size="sm"
            onClick={() => executor.initiateAction(acceptAction)}
            disabled={executor.isExecuting}
            className="flex-1"
          >
            <Check className="h-4 w-4" />
            {acceptAction.label}
          </Button>
        )}

        {rejectAction && (
          <Button
            variant="destructive"
            size="sm"
            onClick={() => executor.initiateAction(rejectAction)}
            disabled={executor.isExecuting}
            className="flex-1"
          >
            <X className="h-4 w-4" />
            {rejectAction.label}
          </Button>
        )}
      </div>

      <ActionConfirmationDialog
        open={executor.showConfirmation}
        action={executor.pendingAction}
        isExecuting={executor.isExecuting}
        onConfirm={executor.confirmAction}
        onCancel={executor.cancelAction}
      />

      {executor.showForm &&
        executor.pendingAction &&
        executor.renderActionForm && (
          <ActionFormDialog
            open={executor.showForm}
            action={executor.pendingAction}
            isExecuting={executor.isExecuting}
            onCancel={executor.cancelAction}
          >
            {executor.renderActionForm({
              action: executor.pendingAction,
              onSubmit: executor.executeWithData,
              onCancel: executor.cancelAction,
              isSubmitting: executor.isExecuting,
            })}
          </ActionFormDialog>
        )}
    </>
  );
}
