'use client';

import { MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type {
  ActionDTO,
  ActionGroupType,
  ObjectDetailDTO,
} from '@/openapi/managerLab.schemas';
import {
  useActionExecutor,
  type ActionFormRenderer,
} from '@/hooks/use-action-executor';
import { useActionFormRenderer } from '@/hooks/use-action-form-renderer';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import { ActionFormDialog } from '@/components/actions/action-form-dialog';

interface ActionsMenuProps {
  actions: ActionDTO[];
  actionGroup: ActionGroupType;
  onActionComplete?: () => void;
  /**
   * Object data to automatically extract default values for forms
   * The registry's extractDefaultValues functions will use this
   */
  objectData?: ObjectDetailDTO;
  /**
   * @deprecated Use the centralized action registry instead.
   * This prop is kept for backward compatibility but will be removed in a future version.
   */
  renderActionForm?: ActionFormRenderer;
  /**
   * Optional custom function to override registry's default value extraction
   * Only needed if you want to customize how defaults are extracted
   */
  getDefaultValues?: (
    action: ActionDTO,
    objectData?: ObjectDetailDTO
  ) => Record<string, unknown> | undefined;
}

export function ActionsMenu({
  actions,
  actionGroup,
  onActionComplete,
  objectData,
  renderActionForm,
  getDefaultValues,
}: ActionsMenuProps) {
  // Use the centralized registry by default
  // It will automatically use extractDefaultValues from registry if objectData is provided
  const registryFormRenderer = useActionFormRenderer(
    objectData,
    getDefaultValues
  );

  // Use custom renderActionForm if provided (for backward compatibility)
  // Otherwise use the registry
  const formRenderer = renderActionForm || registryFormRenderer;

  const executor = useActionExecutor({
    actionGroup,
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
