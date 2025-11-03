'use client';

import { MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { ActionDTO, ActionGroupType } from '@/openapi/managerLab.schemas';
import type { DomainObject } from '@/types/domain-objects';
import { useActionExecutor } from '@/hooks/use-action-executor';
import { useActionFormRenderer } from '@/hooks/use-action-form-renderer';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';

interface ActionsMenuProps {
  actions: ActionDTO[];
  actionGroup: ActionGroupType;
  objectId?: string;
  onActionComplete?: () => void;
  /**
   * Object data to automatically extract default values for forms
   * The registry's render functions will use this
   */
  objectData?: DomainObject;
}

export function ActionsMenu({
  actions,
  actionGroup,
  objectId,
  onActionComplete,
  objectData,
}: ActionsMenuProps) {
  // Use the centralized registry
  const formRenderer = useActionFormRenderer(objectData);

  const executor = useActionExecutor({
    actionGroup,
    objectId,
    renderActionForm: formRenderer,
    onSuccess: () => {
      onActionComplete?.();
    },
  });

  // Filter available actions
  const availableActions = actions.filter(
    (action) => action.available !== false
  );

  if (availableActions.length === 0) {
    return null;
  }

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="icon">
            <MoreHorizontal className="h-5 w-5" />
            <span className="sr-only">Open menu</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {availableActions
            .sort((a, b) => (a.priority || 0) - (b.priority || 0))
            .map((action, index) => (
              <DropdownMenuItem
                key={`${action.action}-${index}`}
                onClick={() => executor.initiateAction(action)}
                className="cursor-pointer"
              >
                {action.label}
              </DropdownMenuItem>
            ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <ActionConfirmationDialog
        open={executor.showConfirmation}
        action={executor.pendingAction}
        isExecuting={executor.isExecuting}
        onConfirm={executor.confirmAction}
        onCancel={executor.cancelAction}
      />

      {executor.pendingAction &&
        executor.renderActionForm &&
        executor.renderActionForm({
          action: executor.pendingAction,
          onSubmit: executor.executeWithData,
          onClose: executor.cancelAction,
          isSubmitting: executor.isExecuting,
          isOpen: executor.showForm,
          actionLabel: executor.pendingAction.label,
        })}
    </>
  );
}
